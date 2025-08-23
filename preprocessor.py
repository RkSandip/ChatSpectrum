import re
import pandas as pd

def preprocess(data):
    # Pattern to split date/time and message
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s'
    messages = re.split(pattern, data)

    if not messages[0].strip():
        messages = messages[1:]

    dates = []
    texts = []

    # Step safely in chunks of 3
    for i in range(0, len(messages)-2, 3):
        date_str = f"{messages[i]},{messages[i+1]}"
        msg = messages[i+2]
        dates.append(date_str.strip())
        texts.append(msg.strip())

    df = pd.DataFrame({'user_message': texts, 'message_date': dates})

    # Flexible parsing for 2-digit and 4-digit years
    def parse_date(x):
        # Remove any trailing dash and spaces
        x = x.strip().rstrip(" -")
        for fmt in ['%d/%m/%Y,%H:%M', '%d/%m/%y,%H:%M']:
            try:
                return pd.to_datetime(x, format=fmt)
            except:
                continue
        return pd.NaT


    df['date'] = df['message_date'].apply(parse_date)
    df.drop(columns=['message_date'], inplace=True)

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

    # Remove media/deleted/empty messages
    df['message'] = df['message'].astype(str).str.strip()
    remove_list = ["<Media omitted>", "This message was deleted", "You deleted this message"]
    df = df[~df["message"].isin(remove_list)]
    df = df[df["message"] != ""].reset_index(drop=True)

    # Extra datetime columns
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Period column
    df['period'] = df['hour'].apply(lambda h: f"{h}-{h+1}" if h < 23 else "23-00")

    return df

