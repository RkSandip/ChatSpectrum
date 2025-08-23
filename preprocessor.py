import re
import pandas as pd

def preprocess(data):
    # Match both 2-digit and 4-digit years
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s'

    # Split messages by date-time pattern
    messages = re.split(pattern, data)
    # messages = ['', day, time, message, day, time, message,...]
    if not messages[0].strip():
        messages = messages[1:]

    dates = []
    texts = []
    for i in range(0, len(messages), 3):
        date_str = f"{messages[i]},{messages[i+1]}"
        msg = messages[i+2]
        dates.append(date_str)
        texts.append(msg)

    df = pd.DataFrame({'user_message': texts, 'message_date': dates})

    # ---------------- Parse dates safely ----------------
    def parse_date(x):
        x = x.strip().rstrip(" -")  # remove trailing dash and spaces
        for fmt in ['%d/%m/%Y,%H:%M', '%d/%m/%y,%H:%M']:
            try:
                return pd.to_datetime(x, format=fmt)
            except:
                continue
        return pd.NaT

    df['date'] = df['message_date'].apply(parse_date)
    df.drop(columns=['message_date'], inplace=True)

    # ---------------- Extract users and messages ----------------
    users = []
    messages_clean = []

    for msg in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', msg, maxsplit=1)
        if len(entry) >= 3:
            users.append(entry[1])
            messages_clean.append(entry[2])
        else:
            users.append('group_notification')
            messages_clean.append(entry[0])

    df['user'] = users
    df['message'] = messages_clean
    df.drop(columns=['user_message'], inplace=True)

    # ---------------- Remove unwanted messages ----------------
    df['message'] = df['message'].astype(str).str.strip()
    remove_list = ["<Media omitted>", "This message was deleted", "You deleted this message"]
    df = df[~df["message"].isin(remove_list)]
    df = df[df["message"] != ""].reset_index(drop=True)

    # ---------------- Extra datetime columns ----------------
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # ---------------- Period column ----------------
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append(f"00-{hour+1}")
        else:
            period.append(f"{hour}-{hour+1}")
    df['period'] = period

    return df
