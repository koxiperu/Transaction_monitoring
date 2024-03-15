import pandas as pd


class TransactionData:
    def __init__(self, data, columns):
        self.df = pd.DataFrame(data, columns=columns)

    @classmethod
    def from_csv(cls, file):
        data = pd.read_csv(file, parse_dates=["created_at"])
        columns = data.columns.tolist()
        return cls(data.to_dict(orient="records"), columns)

    def copy(self):
        return TransactionData(self.df.copy(), self.df.columns.tolist())

    def show_info(self):
        return self.df.info()

    def show_n_rows(self, position, num):
        if num > len(self.df):
            return f"Num must be less than {len(self.df)}."
        if position == "top":
            return self.df.head(num)
        elif position == "bottom":
            return self.df.tail(num)
        else:
            return "position must be 'top' or 'bottom' only"

    def duplicates(self, column):
        try:
            self.df[column]
        except KeyError:
            return f"Column '{column}' doesn't exist"
        except:
            return "Something went wrong"
        else:
            dup = self.df[self.df[column].duplicated(keep=False)]
            if dup.empty:
                return f"No duplicated in column '{column}' found"
            return dup

    def unique_values(self, column):
        try:
            self.df[column]
        except KeyError:
            return f"Column '{column}' doesn't exist"
        except:
            return "Something went wrong"
        else:
            return f"{len(self.df[column].unique())} unique values found in the column {'column'}. \n {self.df[column].unique()}"

    def is_historical(self, column):
        try:
            self.df[column]
        except KeyError:
            return f"Column '{column}' doesn't exist"
        except:
            return "Something went wrong"
        else:
            if self.df[column].dtype == "datetime64[ns]":
                if (self.df[column] > pd.to_datetime("now")).any():
                    return "Future transactions included."
                return "All datetime are historical (in the past)"
            return f"Column '{column}' has NOT datetime type"

    def add_order_amount(self):
        self.df["order_amount"] = self.df["quantity"] * self.df["unit_price"]
        return f"Column 'order_amount' added successfully \n {self.df}"

    def mean(self, col):
        try:
            self.df[col]
        except KeyError:
            return f"Column '{col}' doesn't exist"
        except:
            return "Something went wrong"
        else:
            if (self.df[col].dtype == "float64") | (self.df[col].dtype == "int64"):
                avg_col = self.df[col].mean()
                return f"Average value in column '{col}' is {avg_col.round(2)}"
            return f"Column '{col}' has NOT digital (int, float) type. I can't to calculate average..."


try:
    transactions = TransactionData.from_csv("./data/sample_orders.csv")
except FileNotFoundError:
    print("Can't find the file! Check file path and name.")
except:
    print("Something went wrong...")
else:
    print("File.csv converted to dataframe successfully.")

# print(transactions.show_info())
# print(transactions.show_n_rows('bottom', 999))
# print(transactions.duplicates('isin'))
# print(transactions.unique_values('user_id'))
# print(transactions.is_historical('created_at'))
trc = transactions.copy()
# print(trc.add_order_amount())
# print(trc.mean('user_id'))
