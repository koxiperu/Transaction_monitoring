import pandas as pd
import matplotlib.pyplot as plt

# Subclass of pd.DataFrame for handling transaction data
class TransactionData(pd.DataFrame):
    # Class method to parse CSV file and create TransactionData object
    @classmethod
    def parse_csv(cls, file_path):
        df = pd.read_csv(file_path, parse_dates=["created_at"])
        # Define the set of expected column names
        set_col = set(
            [
                "user_id",
                "created_at",
                "order_type",
                "order_id",
                "isin",
                "quantity",
                "unit_price",
            ]
        )
        # Extract the set of column names from the DataFrame
        set_col_file = set(df.columns)
        # Check if the columns match the expected set of column names
        try:
            if set_col == set_col_file:
                return cls(df)
        except:
            print("Columns defined incorrectly.")
        else:
            print("Columns defined correctly.")
        finally:
            return print("TransactionData object created successfully.")

    # Check if there exists rows with future transactions in date-time column.
    def get_future_transactions(self):
        for col in self.columns:
            # Check if column is datetime type
            if self[col].dtype == "datetime64[ns]":
                # Check if the date in the future
                if (self[col] > pd.to_datetime("now")).any():
                    return self[self[col] > pd.to_datetime("now")]
                return "No future transactions"
        return "No column with date-time type"

    # Show seasonal change of total order values
    def plot_tr_activity(self):
        # Copy dataframe
        df_self = self.copy()
        # Add columns with month number and month name from date-time
        df_self["created_at_month_num"] = df_self["created_at"].dt.month
        df_self["created_at_month_str"] = df_self["created_at"].dt.strftime("%B")
        # Group by number of orders
        df_self = (
            df_self.groupby(["created_at_month_num", "created_at_month_str"])[
                "order_id"
            ]
            .count()
            .reset_index(name="orders")
        )
        # Deviation
        susp_dev = df_self["orders"].std()
        # Average number of orders
        df_self["avg"] = df_self["orders"].mean()
        # Deviation range
        df_self["dev_max"] = df_self["avg"] + susp_dev
        df_self["dev_min"] = df_self["avg"] - susp_dev
        # Draw
        plt.xlabel("Month")
        plt.ylabel("Number of orders")
        plt.title("Seasonal Change of transaction activity")
        plt.plot(
            df_self["created_at_month_str"],
            df_self["avg"],
            color="red",
            label="Average activity",
        )
        plt.plot(
            df_self["created_at_month_str"],
            df_self["dev_max"],
            color="yellow",
            label="Deviation range",
        )
        plt.plot(df_self["created_at_month_str"], df_self["dev_min"], color="yellow")
        plt.bar(df_self["created_at_month_str"], df_self["orders"])
        plt.xticks(df_self["created_at_month_str"], rotation=90)
        plt.legend()
        return plt.show()

    # Find all transactions with order amount greater than max
    def susp_order_amount(self, max):
        df_self = self.copy()
        susp_order = df_self["order_amount"] > max
        # Check if suspicious transactions exist
        if susp_order.any():
            print("Suspicious activity!")
            return df_self[susp_order][
                ["created_at", "user_id", "order_id", "order_amount"]
            ]
        else:
            return "No suspicious activity:))"

    # function that helps to prepare df for frequency analysys
    def make_df(df_set):
        df_self = df_set.copy()
        # Sort transactions by time and user to find suspicious high of frequency among the same user
        df_self = df_self.sort_values(by=["user_id", "created_at"]).reset_index()
        # Time difference (downtime) - time between current transaction and previuos in minutes
        df_self["time_diff"] = (
            df_self["created_at"] - df_self["created_at"].shift(1)
        ).dt.total_seconds() / 60
        # assign 0 to negative and NaN values
        df_self["time_diff"] = df_self["time_diff"].clip(lower=0).fillna(0)
        return df_self

    # Check if there are transactions, between which downtime is less than threshold - high frequency of transactions
    def get_hf_transactions(self, min_freq):
        df_self = self.make_df()
        # Suspicious current transaction - if it happened in short time, less then min_freq,  after previous transaction
        susp_next = df_self[
            (df_self["time_diff"] > 0) & (df_self["time_diff"] < min_freq)
        ]
        # We should remember previous transaction too to inspect it
        susp_prev = df_self.loc[susp_next.index - 1]
        susp_all = pd.concat([susp_prev, susp_next]).sort_values(
            by=["user_id", "created_at"]
        )
        return susp_all[["user_id", "created_at", "order_id", "order_amount"]]

    # Turnover of the fund with isin.
    def plot_fund_turnover(self, isin):
        df_self = self.copy()
        # Sorting values by date
        df_self = df_self.sort_values(by=["created_at"]).reset_index()
        # filter only fund isin
        df_self = df_self[df_self["isin"] == isin]
        # draw
        plt.figure(figsize=(15, 6))
        plt.xlabel("Date")
        plt.ylabel(f"Turnover")
        plt.title(f"Turnover of the fund {isin}")
        plt.bar(df_self["date"], df_self["order_amount"], color="m")
        return plt.show()

    # Downtime of each transaction depending of time
    def plot_activity_increase(self, k):
        df_self = self.copy()
        # Sort transactions by time and user to find suspicious high of frequency among the same user
        df_self = df_self.sort_values(by=["created_at"]).reset_index()
        # Time difference (downtime) - time between current transaction and previuos in minutes
        df_self["time_diff"] = (
            df_self["created_at"] - df_self["created_at"].shift(1)
        ).dt.total_seconds() / 60
        # assign 0 to negative and NaN values
        df_self["time_diff"] = df_self["time_diff"].clip(lower=0).fillna(0)
        df_self = df_self[df_self["time_diff"] > 0]
        # Average downtime
        avg = df_self["time_diff"].mean()
        # Deviation in downtime
        dev = k * df_self["time_diff"].std()
        df_self["avg"] = avg
        # Define deviation range
        df_self["dev_max"] = df_self["avg"] + dev
        df_self["dev_min"] = (df_self["avg"] - dev).clip(lower=0)
        # Draw
        plt.figure(figsize=(15, 6))
        plt.xlabel("Date")
        plt.ylabel("Downtime")
        plt.title("Transaction frequency")
        plt.plot(
            df_self["created_at"],
            df_self["avg"],
            color="red",
            label="Average frequency",
        )
        plt.plot(
            df_self["created_at"],
            df_self["dev_max"],
            color="yellow",
            label="Deviation range",
        )
        plt.plot(df_self["created_at"], df_self["dev_min"], color="yellow")
        plt.bar(df_self["created_at"], df_self["time_diff"])
        plt.legend()
        return plt.show()

    # Find all transactions, that have downtime less than k times deviation from average.
    def activity_increase_susp(self, k):
        df_self = self.make_df()
        # delete first transaction with 0 downtime
        df_sorted = df_self[df_self["time_diff"] > 0]
        # Average downtime
        avg = df_sorted["time_diff"].mean()
        # Deviation in downtime
        dev = k * df_sorted["time_diff"].std()
        # Suspicious current transaction - if it happened in short time, less then min_freq,  after previous transaction
        susp_next = df_self[
            (df_self["time_diff"] > 0) & (df_self["time_diff"] < (avg - dev))
        ]
        # We should remember previous transaction too to inspect it
        susp_prev = df_self.loc[susp_next.index - 1]
        susp_all = pd.concat([susp_prev, susp_next]).sort_values(
            by=["user_id", "created_at"]
        )
        if susp_next.empty:
            return "No suspicious increase of activity."
        return susp_all

    # Dependence of the number of suspicious transactions on the deviation factor
    def plot_dev_factor_act_increase(self):
        # Do the same: sort by date, calculate downtime (time difference between current and previous transaction), change all Nan on 0, take only positive downtimes
        df_self = self.copy()
        df_self = df_self.sort_values(by=["created_at"]).reset_index()
        df_self["time_diff"] = (
            df_self["created_at"] - df_self["created_at"].shift(1)
        ).dt.total_seconds() / 60
        df_self["time_diff"] = df_self["time_diff"].fillna(0)
        df_sorted = df_self[df_self["time_diff"] > 0]
        # Average time difference (downtime)
        avg = df_sorted["time_diff"].mean()
        factors = [i * 0.001 for i in range(1000)]
        effect = []
        # For factors from 0 to 1 check, how much suspicious transactions we have in %. Save in the list 'effect'
        for i in factors:
            susp_dev = df_sorted["time_diff"].std()
            df_susp = df_sorted[(df_sorted["time_diff"] - avg) < 0 - i * susp_dev]
            effect.append(len(df_susp) * 100 / len(self))
        # make df from two lists.
        df_factor = pd.DataFrame({"factor": factors, "effect": effect})
        # Draw
        plt.figure(figsize=(15, 6))
        plt.xlabel("factor")
        plt.ylabel("%% of suspicious decrease of downtime")
        plt.title("Dependence the suspicious activity increase on deviation factor")
        plt.plot(df_factor["factor"], df_factor["effect"], color="green")
        return plt.show()

    # Dependence of total order amount on time
    def plot_order_amount(self, k):
        dset = self.copy()
        # Find average and deviation range in order amount
        avg = dset["order_amount"].mean()
        dev = k * dset["order_amount"].std()
        dset["avg"] = avg
        dset["dev_max"] = dset["avg"] + dev
        dset["dev_min"] = (dset["avg"] - dev).clip(lower=0)
        # Draw
        plt.figure(figsize=(15, 6))
        plt.xlabel("Date")
        plt.ylabel("Total order amount")
        plt.title("Change of total order amount")
        plt.bar(dset["created_at"], dset["order_amount"])
        plt.plot(
            dset["created_at"], dset["avg"], color="red", label="Average order amount"
        )
        plt.plot(
            dset["created_at"], dset["dev_max"], color="yellow", label="Deviation range"
        )
        plt.plot(dset["created_at"], dset["dev_min"], color="yellow")
        plt.legend()
        return plt.show()

    # Find transactions with suspiciously big order amount
    def order_amount_susp(self, k):
        df_self = self.copy()
        # Average and deviation
        avg = df_self["order_amount"].mean()
        dev = k * df_self["order_amount"].std()
        # Find transactions only with order amount higher than maximum of deviation range
        df_susp = df_self[(self["order_amount"] - avg) > dev]
        if df_susp.empty:
            return "No suspicious transactions deviating from the norm"
        return df_susp[["created_at", "user_id", "order_id", "order_amount"]]

    # # Dependence of the number of suspicious transactions on the deviation factor
    def plot_dev_factor_order_amount(self):
        df_self = self.copy()
        avg = df_self["order_amount"].mean()
        factors = [i * 0.01 for i in range(400)]
        effect = []
        # For factors from 0.01 to 4 check, how much suspicious transactions we have in %. Save in the list 'effect'
        for i in factors:
            dev = df_self["order_amount"].std()
            df_susp = df_self[(df_self["order_amount"] - avg) > i * dev]
            effect.append(len(df_susp) * 100 / len(self))
        df_factor = pd.DataFrame({"factor": factors, "effect": effect})
        # Draw
        plt.figure(figsize=(15, 6))
        plt.xlabel("factor")
        plt.ylabel("%% of suspicious orders")
        plt.title("Dependence the suspicious order amount on deviation factor")
        plt.plot(df_factor["factor"], df_factor["effect"], color="green")
        return plt.show()

    # For one user find his dependence of order amount on time
    def plot_user_order_amount(self, user, k):
        df_self = self.copy()
        # Filter only one user
        df_user = df_self[df_self["user_id"] == user].reset_index()
        # Find average order amount and deviation range
        avg = df_user["order_amount"].mean()
        dev = k * df_user["order_amount"].std()
        df_user["avg"] = avg
        df_user["dev_max"] = df_user["avg"] + dev
        df_user["dev_min"] = (df_user["avg"] - dev).clip(lower=0)
        # Draw
        plt.figure(figsize=(15, 6))
        plt.xlabel("Date")
        plt.ylabel("Order amount")
        plt.title(f"User {user} with his total order amount pattern")
        plt.plot(
            df_user["created_at"],
            df_user["avg"],
            color="red",
            label="Average order amount",
        )
        plt.plot(
            df_user["created_at"],
            df_user["dev_max"],
            color="yellow",
            label="Deviation range",
        )
        plt.plot(df_user["created_at"], df_user["dev_min"], color="yellow")
        plt.bar(df_user["created_at"], df_user["order_amount"], bottom=0)
        plt.legend()
        return plt.show()

    # For definit user find suspicious transactions based on order amount
    def user_order_amount_susp(self, user, k):
        df_self = self.copy()
        # Filter our user
        df_user = df_self[df_self["user_id"] == user]
        avg = df_user["order_amount"].mean()
        dev = k * df_user["order_amount"].std()
        df_susp = df_user[(df_user["order_amount"] - avg) > dev]
        if df_susp.empty:
            return f"No suspicious transactions deviating from the norm for user {user}"
        return df_susp[["created_at", "order_id", "order_amount"]]

    # find transactions, that for the same user, for the same fund on the same date has two types: BUY and SELL.
    def susp_circ(self):
        df_copy = self.copy()
        # take date from datetime column
        df_copy["date"] = df_copy["created_at"].dt.date
        # Group by date, isin and user and count number of different order_types. If it's only 1 - not suspicious, if 2 (BUY and SELL), we need to check further
        df_gr_by_user = (
            df_copy.groupby(["user_id", "isin", "date"])["order_type"]
            .nunique()
            .reset_index()
        )
        df_susp = df_gr_by_user[df_gr_by_user["order_type"] > 1]
        if df_susp.empty:
            return "No suspicious transactions"
        else:
            # Make beautiful table for transactions on the same date, isin and user, but with different order types.
            df_aid = (
                df_copy.groupby(["user_id", "isin", "date", "order_type"])[
                    "order_amount"
                ]
                .sum()
                .reset_index()
            )
            df_susp = df_susp.rename(columns={"order_type": "types"})
            df_susp = df_susp.merge(df_aid, on=["user_id", "isin", "date"], how="left")
            df_susp = df_susp.drop(columns=["types"])
            return df_susp

    # Frequency of transactions for one user
    def plot_activity_increase_user(self, user, k):
        df_self = self.make_df()
        df_activ = (
            df_self[df_self["time_diff"] > 0]
            .groupby(["user_id"])["time_diff"]
            .agg(["mean", "std"])
        )
        df_full = pd.merge(df_self, df_activ, on="user_id", how="left")
        df_full["dev_max"] = df_full["mean"] + k * df_full["std"]
        df_full["dev_min"] = (df_full["mean"] - k * df_full["std"]).clip(lower=0)
        df_full = df_full[df_full["user_id"] == user]
        # Draw
        plt.figure(figsize=(15, 6))
        plt.xlabel("Date")
        plt.ylabel("Downtime")
        plt.title("Speed of user's activity")
        plt.bar(df_full["created_at"], df_full["time_diff"], bottom=0)
        plt.plot(
            df_full["created_at"],
            df_full["mean"],
            color="red",
            label="Average downtime",
        )
        plt.plot(
            df_full["created_at"],
            df_full["dev_max"],
            color="yellow",
            label="Deviation range",
        )
        plt.plot(df_full["created_at"], df_full["dev_min"], color="yellow")
        plt.legend()
        df_susp_rapid = df_full[
            (df_full["time_diff"] < df_full["dev_min"]) & (df_full["time_diff"] > 0)
        ]
        return plt.show()
