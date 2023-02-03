import requests
import numpy as np
import pandas as pd

def get_total_revenue(data):
    revenue_data = data['annualReports']
    sorted_revenue_data = sorted(revenue_data, key=lambda x: x["fiscalDateEnding"], reverse=True)

    rev_growth = (int(sorted_revenue_data[0]['totalRevenue']) - int(sorted_revenue_data[1]['totalRevenue']))/int(sorted_revenue_data[1]['totalRevenue'])

    return rev_growth

API_key = "2IN2Q6KL5TUZF8B3" # Still move this API Key to environment variables
symbol = "TSLA"

url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={API_key}'
r = requests.get(url)
data = r.json()

rev_growth = get_total_revenue(data)

print("revenue growth:", rev_growth)
# Test with the balance sheet 

# Turn it into a pandas dataframe

# Income statement

revenue_data = data['annualReports']
sorted_revenue_data = sorted(revenue_data, key=lambda x: x["fiscalDateEnding"], reverse=True)
income_statement = pd.DataFrame.from_dict(sorted_revenue_data[0], orient= 'index')

income_statement.columns = ['current_year']
# income_statement['as_%_of_revenue'] = income_statement / income_statement.iloc[0]
income_statement.drop(income_statement.index[:2], inplace=True)
# income_statement = income_statement.dropna() None is as a string type here

income_statement = income_statement[income_statement.current_year != 'None']

income_statement = income_statement.applymap(lambda x: int(x))

income_statement['as_%_of_revenue'] = income_statement / income_statement.loc["totalRevenue"]

#forecasting 5 next years income statement
income_statement['next_year'] =  (income_statement['current_year']['totalRevenue'] * (1+rev_growth)) * income_statement['as_%_of_revenue'] 
income_statement['next_2_year'] =  (income_statement['next_year']['totalRevenue'] * (1+rev_growth)) * income_statement['as_%_of_revenue'] 
income_statement['next_3_year'] =  (income_statement['next_2_year']['totalRevenue'] * (1+rev_growth)) * income_statement['as_%_of_revenue'] 
income_statement['next_4_year'] =  (income_statement['next_3_year']['totalRevenue'] * (1+rev_growth)) * income_statement['as_%_of_revenue'] 
income_statement['next_5_year'] =  (income_statement['next_4_year']['totalRevenue'] * (1+rev_growth)) * income_statement['as_%_of_revenue']

print(income_statement)

url2 = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={API_key}'

r2 = requests.get(url2)
data2 = r2.json()

revenue_data = data2['annualReports']
sorted_revenue_data = sorted(revenue_data, key=lambda x: x["fiscalDateEnding"], reverse=True)
balance_sheet = pd.DataFrame.from_dict(sorted_revenue_data[0], orient= 'index')

balance_sheet.columns = ['current_year']
# income_statement['as_%_of_revenue'] = income_statement / income_statement.iloc[0]
balance_sheet.drop(balance_sheet.index[:2], inplace=True)
# income_statement = income_statement.dropna() None is as a string type here

balance_sheet = balance_sheet[balance_sheet.current_year != 'None']

balance_sheet = balance_sheet.applymap(lambda x: int(x))

balance_sheet['as_%_of_revenue'] = balance_sheet / income_statement["current_year"].loc["totalRevenue"]

#forecasting the next 5 years Balance Sheet.
balance_sheet['next_year'] =  income_statement['next_year'] ['totalRevenue'] * balance_sheet['as_%_of_revenue']
balance_sheet['next_2_year'] =  income_statement['next_2_year'] ['totalRevenue'] * balance_sheet['as_%_of_revenue']
balance_sheet['next_3_year'] =  income_statement['next_3_year']['totalRevenue'] * balance_sheet['as_%_of_revenue'] 
balance_sheet['next_4_year'] =  income_statement['next_4_year']['totalRevenue']  * balance_sheet['as_%_of_revenue'] 
balance_sheet['next_5_year'] =  income_statement['next_5_year']['totalRevenue'] * balance_sheet['as_%_of_revenue']

# # Just sort it to be sure!
# # What is the time complexity of sorting an already sorted list --> maybe a weird question
# print(data)

print(income_statement)
print(balance_sheet)

CF_forecast = {}
CF_forecast['next_year'] = {}
CF_forecast['next_year']['netIncome'] = income_statement['next_year']['netIncome']
CF_forecast['next_year']['inc_depreciation'] = income_statement['next_year']['depreciationAndAmortization'] - income_statement['current_year']['depreciationAndAmortization']
CF_forecast['next_year']['inc_receivables'] = balance_sheet['next_year']['currentNetReceivables'] - balance_sheet['current_year']['currentNetReceivables']
CF_forecast['next_year']['inc_inventory'] = balance_sheet['next_year']['inventory'] - balance_sheet['current_year']['inventory']
CF_forecast['next_year']['inc_payables'] = balance_sheet['next_year']['deferredRevenue'] - balance_sheet['current_year']['deferredRevenue']
CF_forecast['next_year']['CF_operations'] = CF_forecast['next_year']['netIncome'] + CF_forecast['next_year']['inc_depreciation'] + (CF_forecast['next_year']['inc_receivables'] * -1) + (CF_forecast['next_year']['inc_inventory'] *-1) + CF_forecast['next_year']['inc_payables']
CF_forecast['next_year']['CAPEX'] = balance_sheet['next_year']['propertyPlantEquipment'] - balance_sheet['current_year']['propertyPlantEquipment'] + income_statement['next_year']['depreciationAndAmortization']
CF_forecast['next_year']['FCF'] = CF_forecast['next_year']['CAPEX'] + CF_forecast['next_year']['CF_operations']
CF_forecast['next_2_year'] = {}
CF_forecast['next_2_year']['netIncome'] = income_statement['next_2_year']['netIncome']
CF_forecast['next_2_year']['inc_depreciation'] = income_statement['next_2_year']['depreciationAndAmortization'] - income_statement['next_year']['depreciationAndAmortization']
CF_forecast['next_2_year']['inc_receivables'] = balance_sheet['next_2_year']['currentNetReceivables'] - balance_sheet['next_year']['currentNetReceivables']
CF_forecast['next_2_year']['inc_inventory'] = balance_sheet['next_2_year']['inventory'] - balance_sheet['next_year']['inventory']
CF_forecast['next_2_year']['inc_payables'] = balance_sheet['next_2_year']['deferredRevenue'] - balance_sheet['next_year']['deferredRevenue']
CF_forecast['next_2_year']['CF_operations'] = CF_forecast['next_2_year']['netIncome'] + CF_forecast['next_2_year']['inc_depreciation'] + (CF_forecast['next_2_year']['inc_receivables'] * -1) + (CF_forecast['next_2_year']['inc_inventory'] *-1) + CF_forecast['next_2_year']['inc_payables']
CF_forecast['next_2_year']['CAPEX'] = balance_sheet['next_2_year']['propertyPlantEquipment'] - balance_sheet['next_year']['propertyPlantEquipment'] + income_statement['next_2_year']['depreciationAndAmortization']
CF_forecast['next_2_year']['FCF'] = CF_forecast['next_2_year']['CAPEX'] + CF_forecast['next_2_year']['CF_operations']
CF_forecast['next_3_year'] = {}
CF_forecast['next_3_year']['netIncome'] = income_statement['next_3_year']['netIncome']
CF_forecast['next_3_year']['inc_depreciation'] = income_statement['next_3_year']['depreciationAndAmortization'] - income_statement['next_2_year']['depreciationAndAmortization']
CF_forecast['next_3_year']['inc_receivables'] = balance_sheet['next_3_year']['currentNetReceivables'] - balance_sheet['next_2_year']['currentNetReceivables']
CF_forecast['next_3_year']['inc_inventory'] = balance_sheet['next_3_year']['inventory'] - balance_sheet['next_2_year']['inventory']
CF_forecast['next_3_year']['inc_payables'] = balance_sheet['next_3_year']['deferredRevenue'] - balance_sheet['next_2_year']['deferredRevenue']
CF_forecast['next_3_year']['CF_operations'] = CF_forecast['next_3_year']['netIncome'] + CF_forecast['next_3_year']['inc_depreciation'] + (CF_forecast['next_3_year']['inc_receivables'] * -1) + (CF_forecast['next_3_year']['inc_inventory'] *-1) + CF_forecast['next_3_year']['inc_payables']
CF_forecast['next_3_year']['CAPEX'] = balance_sheet['next_3_year']['propertyPlantEquipment'] - balance_sheet['next_2_year']['propertyPlantEquipment'] + income_statement['next_3_year']['depreciationAndAmortization']
CF_forecast['next_3_year']['FCF'] = CF_forecast['next_3_year']['CAPEX'] + CF_forecast['next_3_year']['CF_operations']
CF_forecast['next_4_year'] = {}
CF_forecast['next_4_year']['netIncome'] = income_statement['next_4_year']['netIncome']
CF_forecast['next_4_year']['inc_depreciation'] = income_statement['next_4_year']['depreciationAndAmortization'] - income_statement['next_3_year']['depreciationAndAmortization']
CF_forecast['next_4_year']['inc_receivables'] = balance_sheet['next_4_year']['currentNetReceivables'] - balance_sheet['next_3_year']['currentNetReceivables']
CF_forecast['next_4_year']['inc_inventory'] = balance_sheet['next_4_year']['inventory'] - balance_sheet['next_3_year']['inventory']
CF_forecast['next_4_year']['inc_payables'] = balance_sheet['next_4_year']['deferredRevenue'] - balance_sheet['next_3_year']['deferredRevenue']
CF_forecast['next_4_year']['CF_operations'] = CF_forecast['next_4_year']['netIncome'] + CF_forecast['next_4_year']['inc_depreciation'] + (CF_forecast['next_4_year']['inc_receivables'] * -1) + (CF_forecast['next_4_year']['inc_inventory'] *-1) + CF_forecast['next_4_year']['inc_payables']
CF_forecast['next_4_year']['CAPEX'] = balance_sheet['next_4_year']['propertyPlantEquipment'] - balance_sheet['next_3_year']['propertyPlantEquipment'] + income_statement['next_4_year']['depreciationAndAmortization']
CF_forecast['next_4_year']['FCF'] = CF_forecast['next_4_year']['CAPEX'] + CF_forecast['next_4_year']['CF_operations']
CF_forecast['next_5_year'] = {}
CF_forecast['next_5_year']['netIncome'] = income_statement['next_5_year']['netIncome']
CF_forecast['next_5_year']['inc_depreciation'] = income_statement['next_5_year']['depreciationAndAmortization'] - income_statement['next_4_year']['depreciationAndAmortization']
CF_forecast['next_5_year']['inc_receivables'] = balance_sheet['next_5_year']['currentNetReceivables'] - balance_sheet['next_4_year']['currentNetReceivables']
CF_forecast['next_5_year']['inc_inventory'] = balance_sheet['next_5_year']['inventory'] - balance_sheet['next_4_year']['inventory']
CF_forecast['next_5_year']['inc_payables'] = balance_sheet['next_5_year']['deferredRevenue'] - balance_sheet['next_4_year']['deferredRevenue']
CF_forecast['next_5_year']['CF_operations'] = CF_forecast['next_5_year']['netIncome'] + CF_forecast['next_5_year']['inc_depreciation'] + (CF_forecast['next_5_year']['inc_receivables'] * -1) + (CF_forecast['next_5_year']['inc_inventory'] *-1) + CF_forecast['next_5_year']['inc_payables']
CF_forecast['next_5_year']['CAPEX'] = balance_sheet['next_5_year']['propertyPlantEquipment'] - balance_sheet['next_4_year']['propertyPlantEquipment'] + income_statement['next_5_year']['depreciationAndAmortization']
CF_forecast['next_5_year']['FCF'] = CF_forecast['next_5_year']['CAPEX'] + CF_forecast['next_5_year']['CF_operations']


#add the forecasted cash flows into a Pandas
CF_forec = pd.DataFrame.from_dict(CF_forecast,orient='columns')
#add below option to format the dataframe with thousand separators
pd.options.display.float_format = '{:,.0f}'.format
print(CF_forec)

# Still present mu WACC calculations here