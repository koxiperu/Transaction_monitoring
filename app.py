import numpy as np
from transaction import TransactionData


def process_orders(file_path):
    # 1. File processing
    df = TransactionData.parse_csv(file_path)
    # 2. Basic analysis
        # 2.1. Total number of orders
    print(f'Number of orders: {len(df)}')
        # 2.2. Number of unique clients
    unq = df['user_id'].nunique()
    print(f"Number of unique users: {unq}")
        # 2.3. Average order amount
    df['order_amount'] = df['quantity']*df['unit_price']
    avg_order_amount = df['order_amount'].mean()
    print(f"Average order amount: {avg_order_amount.round(2)}")
        # 2.4. Average number of orders per day
    df['date'] = df['created_at'].dt.date
    tr_per_day = df.groupby(df['date']).size().reset_index(name='number_of_orders')
    print(f"Number of transactions per day: \n {tr_per_day}")
    avg_tr_per_day = tr_per_day['number_of_orders'].mean()
    avg_dict = {'Average number of orders per day': avg_tr_per_day, 'Rounded up to integer': np.ceil(avg_tr_per_day).astype(int), 'Rounded down to integer': np.floor(avg_tr_per_day).astype(int), 'Rounded up to 3rd decimal':np.ceil(avg_tr_per_day*1000)/1000, 'Rounded down to 3rd decimal':np.floor(avg_tr_per_day*1000)/1000}
    print(avg_dict)
        # 2.5. Bonus
    print(df.info())
    dup = df[df.duplicated(keep=False)]
    print(f"Duplicates {dup}")
    print("Order type has only values: ", df['order_type'].unique())
    df.get_future_transactions()
    # 3. Advanced analysis
        # 3.1. Standart deviation of the order amount
    print(f"Average order amount: {round(avg_order_amount,2)}")
    dev_order_amount = df['order_amount'].std()
    print(f"Standart deviation of the order amount: {round(dev_order_amount,2)}")
        # 3.2. Total value of orders per client
            # 3.2.1. Turnover
    client_abs_value = df.groupby(['user_id'])['order_amount'].sum().reset_index(name='turnover')
    print(f"Turnover: {client_abs_value}")
            # 3.2.2. Balance (debit - credit)
    pivot_user = df.pivot_table(index='user_id', columns='order_type', values='order_amount', aggfunc='sum', fill_value=0)
    pivot_user['balance']=pivot_user['BUY']-pivot_user['SELL']
    print(pivot_user)
        # 3.3. Bonus
            # 3.3.1. Additional info about dataframe
    df.describe()
            # 3.3.2. Seasonal change of total orders value (transaction activity)
    df.plot_tr_activity()
            # 3.3.3. Total value of orders per day
    per_date = df.groupby('date')['order_amount'].sum().reset_index(name='turnover')
    print(per_date)
            # 3.3.4. Total value of orders per fund (balance)
    pivot_isin = df.pivot_table(index='isin', columns='order_type', values='order_amount', aggfunc='sum', fill_value=0).rename_axis(None, axis=1)
    pivot_isin['balance']=pivot_isin['BUY']-pivot_isin['SELL']
    print(pivot_isin)
    # 4. Suspicious Transactions
        # 4.1. Order value > n
    df.susp_order_amount(9500)
        # 4.2. High frequency orders (threshold in minutes)
    df.get_hf_transactions(180)
        # 4.3. Bonus: Change of the fund's turnover
    df.plot_fund_turnover('LU98163828108')
    # 5. Suspicious Transactions (Advanced)
        # 5.1. Rapid increase in account activity
            # 5.1.1. Change of downtime (pattern)
    df.plot_activity_increase(0.9)
            # 5.1.2. Suspicious decrease of downtime (rapid increase in activity)
    df.activity_increase_susp(0.845)
            # 5.1.3. How to choose deviation factor (width of the normal range for downtime)
    df.plot_dev_factor_act_increase()
        # 5.2. Suspicious value of orders
            # 5.2.1. Change of total value of orders (pattern)
    df.plot_order_amount(1)
            # 5.2.2. Suspiciously high order amount
    df.order_amount_susp(3)
            # 5.2.3. How to choose deviation factor (width of the normal range for order amount)
    df.plot_dev_factor_order_amount()
        # 5.3. Bonus
            # 5.3.1. User's suspicious value of his orders
                # 5.3.1.1. Order amount of the user with deviation range (pattern)
    df.plot_user_order_amount('user|n4jjtiirlddz2b2lryq8lucl',1)
                # 5.3.1.2. Suspicious order amount for the user
    df.user_order_amount_susp('user|n4jjtiirlddz2b2lryq8lucl',2)
                # 5.3.2. Suspicious circular trading
    df.susp_circ()
                # 5.3.3. Frequency of transactions for one user
    df.plot_activity_increase_user('user|57f4lb88pr59ukwzm8gpp2c5', 1)


if __name__=='__main__':
    process_orders("./data/sample_orders_2.csv")
