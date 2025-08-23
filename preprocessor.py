import re
import pandas as pd

def preprocess(data):
    # Regex: split messages by date/time
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s'

    split_data = re.split(pattern, data)
    if not split_data[0].strip():
        split_data = split_data[1:]

    dates = []
    messages = []
    for i in range(0, len(split_data), 3):
        try:
            date_str = f"{split_data[i]},{split_data[i+1]}"
            msg = split_data[i+2]
        except IndexError:
            continue
        dates.append(date_str.strip())
        messages.append(msg.strip())

    df = pd.DataFrame({'raw_message': messages, 'message_date': dates})

    # ----- Safe date parsing -----
    def parse_date(x):
        x = x.strip().rstrip(" -")
        # Try both 4-digit and 2-digit year formats
        for fmt in ['%d/%m/%Y,%H:%M', '%d/%m/%y,%H:%M']:
            try:
                return pd.to_datetime(x, format=fmt)
            except:
                continue
        return pd.NaT

    df['date'] = df['message_date'].apply(parse_date)
    df.drop(columns=['message_date'], inplace=True)

    # ----- Extract users -----
    users = []
    clean_messages = []
    for msg in df['raw_message']:
        entry = re.split(r'([\w\W]+?):\s', msg, maxsplit=1)
        if len(entry) >= 3:
            users.append(entry[1].strip())
            clean_messages.append(entry[2].strip())
        else:
            users.append('group_notification')
            clean_messages.append(msg.strip())

    df['user'] = users
    df['message'] = clean_messages
    df.drop(columns=['raw_message'], inplace=True)

    # ----- Remove unwanted messages -----
    remove_list = ["<Media omitted>", "This message was deleted", "You deleted this message"]
    df = df[~df["message"].isin(remove_list)]
    df = df[df["message"] != ""].reset_index(drop=True)

    # ----- Extra datetime columns -----
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # ----- Period column -----
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
