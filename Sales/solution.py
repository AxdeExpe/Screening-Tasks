import pandas as pd
import os

def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')

class SalesVolume:

    def __init__(self, path):

        if os.path.exists(path):
            self.df_sales = pd.read_csv(path)

            self.df_sales['date'] = pd.to_datetime(self.df_sales['date'], errors='coerce')  # fehlerhafte -> NaT
            self.df_sales['product_id'] = pd.to_numeric(self.df_sales['product_id'], errors='coerce', downcast='integer')
            self.df_sales['units_sold'] = pd.to_numeric(self.df_sales['units_sold'], errors='coerce', downcast='integer')
            self.df_sales['price_per_unit'] = pd.to_numeric(self.df_sales['price_per_unit'], errors='coerce', downcast='float')

            self.df_sales.dropna(subset=['date', 'product_id', 'units_sold', 'price_per_unit'], inplace=True)

            self.df_sales.reset_index(drop=True, inplace=True)

            self.df_sales['volume'] = self.df_sales['units_sold'] * self.df_sales['price_per_unit']

            print(self.df_sales)
        else:
            raise Exception("File does not exist")

        return
    
    
    def get_monthly_volume_by_product(self):

        self.df_sales['month'] = self.df_sales['date'].dt.to_period('M')
        df_sales_monthly = self.df_sales.groupby(['month','product_id'])['volume'].sum().reset_index()

        return df_sales_monthly
    
    def get_top_n(self, n, sort_criteria='volume_change_absolute'):

        if sort_criteria not in ['volume_change_absolute', 'volume_change_relative']:
            raise Exception("sort_criteria must be 'volume_change_absolute' or 'volume_change_relative'")
        
        if not isinstance(n, int):
            raise Exception("n must be an integer")

        df_sales_monthly = self.get_monthly_volume_by_product()

        df_sales_monthly['prev_month_volume'] = df_sales_monthly.groupby('product_id')['volume'].shift(1)
        df_sales_monthly['volume_change_absolute'] = df_sales_monthly['volume'] - df_sales_monthly['prev_month_volume']
        df_sales_monthly['volume_change_relative'] = df_sales_monthly.apply(
            lambda x: (x['volume']/x['prev_month_volume']*100) if x['prev_month_volume'] else 0, axis=1
        )

        top_n = df_sales_monthly.sort_values(sort_criteria, ascending=False).head(n)

        return top_n
    

if __name__ == "__main__":

    sales = SalesVolume("data.csv")
    print_full(sales.get_monthly_volume_by_product())

    print_full(sales.get_top_n(5))
