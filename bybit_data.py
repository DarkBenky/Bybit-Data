import bybit
import pandas as pd
import time
import pandas as pd
import datetime as dt
import sqlite3 as sql
# import data_formating
# import page_backend
# import ta
# import goose
import ByBit_API as API
import threading
import app
# import plotly.graph_objects as go


def str_to_round(number):
	try:
		if float(number) < 1:
			return float(number)
		return round(float(number))
	except Exception as e:
		print("Error: ", e)


def log_error(error_massage:str):
	try:
		with open("error.txt", "r") as file:
			print("file exists")
			now = dt.datetime.now()
			now = now.strftime("%Y-%m-%d %H:%M:%S")
			file.write(now+"\n"+error_massage+"\n")
	except:
		print("file does not exist")
		now = dt.datetime.now()
		now = now.strftime("%Y-%m-%d %H:%M:%S")
		with open("error.txt", "w") as file:
			file.write(now+"\n"+error_massage+"\n")
			
def get_logs():
	try:
		data = []
		with open("bybit-upgrade.csv", "r") as file:
			lines = file.readlines()
			lines = lines[-61:]
			for line in lines:
				split = line.split(",")
				split.pop(0)
				data.append(split)
		return data[:60]
	except Exception as e:
		print("Error: ", e)
		log_error(str(e))

def average_price(formatted_data,price):
	try:
		prices = goose.select_data_at_index(formatted_data, 1)
		prices = [float(i) for i in prices]
		prices.append(float(price))
		average_price = sum(prices) / len(prices)
		return average_price
	except:
		print("average_price error")

def average_volume(formatted_data):
	try:
		volumes = goose.select_data_at_index(formatted_data, 11)
		volumes = [float(i) for i in volumes]
		average_volume = sum(volumes) / len(volumes)
		return average_volume
	except:
		print("average_volume error")

def average_direction(formatted_data,p):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(p))
		direction = 0
		for i in range(1, len(price)-1):
			if price[i] > price[i-1]:
				direction += price[i] - price[i-1]
			else:
				direction -= price[i-1] - price[i]
		return direction/len(price)
	except:
		print("average_direction error")

def POC(formatted_data):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		volume = goose.select_data_at_index(formatted_data, 11)
		volume = [float(i) for i in volume]
		POC = {}
		for i in range(0, len(price)):
			current_price = round(price[i],-1)
			if current_price in POC:
				POC[current_price] += abs(volume[i])
			else:
				POC[current_price] = abs(volume[i])
		POC = sorted(POC.items(), key=lambda x: x[1], reverse=True)
		return POC[0][0]
	except:
		print("POC error")

def TPO(formatted_data,p):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(p))
		TPO = {}
		for i in range(0, len(price)):
			current_price = round(price[i],-1)
			if current_price in TPO:
				TPO[current_price] += 1
			else:
				TPO[current_price] = 1
		TPO = sorted(TPO.items(), key=lambda x: x[1], reverse=True)
		return TPO[0][0]
	except:
		print("TPO error")

def VWAP(formatted_data):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		volume = goose.select_data_at_index(formatted_data, 11)
		volume = [float(i) for i in volume]
		VWAP = 0
		for i in range(0, len(price)):
			VWAP += price[i] * volume[i]
		VWAP = VWAP / sum(volume)
		return VWAP
	except:
		print("VWAP error")

def RSI(formatted_data,prices):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(prices))
		gain = 0
		loss = 0
		for i in range(1, len(price)):
			if price[i] > price[i-1]:
				gain += price[i] - price[i-1]
			else:
				loss += price[i-1] - price[i]
		avg_gain = gain / len(price)
		avg_loss = loss / len(price)
		RSI = 100 - (100 / (1 + (avg_gain / avg_loss)))
		return RSI
	except:
		print("RSI error")
	

def MACD(formatted_data,p):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(p))
		EMA_12 = 0
		EMA_26 = 0
		for i in range(0, 12):
			EMA_12 += price[i]
		EMA_12 = EMA_12 / 12
		for i in range(0, 26):
			EMA_26 += price[i]
		EMA_26 = EMA_26 / 26
		for i in range(12, len(price)):
			EMA_12 = (price[i] * 2 / 13) + (EMA_12 * 11 / 13)
		for i in range(26, len(price)):
			EMA_26 = (price[i] * 2 / 27) + (EMA_26 * 25 / 27)
		MACD = EMA_12 - EMA_26
		return MACD
	except:
		print("MACD error")

def OBV(formatted_data):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		volume = goose.select_data_at_index(formatted_data, 11)
		volume = [float(i) for i in volume]
		OBV = 0
		for i in range(1, len(price)):
			if price[i] > price[i-1]:
				OBV += volume[i]
			else:
				OBV -= volume[i]
		return OBV
	except:
		print("OBV error")

def Volume(formatted_data):
	try:
		volume = goose.select_data_at_index(formatted_data, 7)
		volume = [float(i) for i in volume]
		print(abs(volume[-1]) - abs(volume[-2]))
		return abs(volume[-1]) - abs(volume[-2])
	except:
		print("Volume error")

def boulanger_bands(formatted_data,p):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(p))
		EMA_20 = 0
		for i in range(0, 20):
			EMA_20 += price[i]
		EMA_20 = EMA_20 / 20
		for i in range(20, len(price)):
			EMA_20 = (price[i] * 2 / 21) + (EMA_20 * 19 / 21)
		SD = 0
		for i in range(0, 20):
			SD += (price[i] - EMA_20) ** 2
		SD = (SD / 20) ** 0.5
		return EMA_20 + 2 * SD, EMA_20, EMA_20 - 2 * SD
	except:
		print("Boulanger Bands error")

def change_of_trend(formatted_data,prices):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(prices))
		EMA_20 = 0
		for i in range(0, 20):
			EMA_20 += price[i]
		EMA_20 = EMA_20 / 20
		for i in range(20, len(price)):
			EMA_20 = (price[i] * 2 / 21) + (EMA_20 * 19 / 21)
		SD = 0
		for i in range(0, 20):
			SD += (price[i] - EMA_20) ** 2
		SD = (SD / 20) ** 0.5
		if price[-1] > EMA_20 + 2 * SD:
			return 1 , 0 , 0
		elif price[-1] < EMA_20 - 2 * SD:
			return 0 , 1 , 0
		else:
			return 0 , 0 , 1
	except:
		print("Change of Trend error")

def price_pattern(formatted_data , price):
	try:
		prices = goose.select_data_at_index(formatted_data, 1)
		prices = [float(i) for i in prices]
		prices.append(float(price))
		price = float(price)
		if prices[-1] > prices[-2] > prices[-3] and price > prices[-1] and price > prices[-2]:
			return 1 , 0 , 0
		elif prices[-1] < prices[-2] < prices[-3] and price < prices[-1] and price < prices[-2]:
			return 0 , 1 , 0
		else:
			return 0 , 0 , 1
	except Exception as e:
		print(e)
		print("Price Pattern error")

def MA_cross(formatted_data,price):
	try:
		prices = goose.select_data_at_index(formatted_data, 1)
		prices = [float(i) for i in prices]
		prices.append(float(price))
		EMA_20 = 0
		for i in range(0, 20):
			EMA_20 += prices[i]
		EMA_20 = EMA_20 / 20
		for i in range(20, len(prices)):
			EMA_20 = (prices[i] * 2 / 21) + (EMA_20 * 19 / 21)
		EMA_50 = 0
		for i in range(0, 50):
			EMA_50 += prices[i]
		EMA_50 = EMA_50 / 50
		for i in range(50, len(prices)):
			EMA_50 = (prices[i] * 2 / 51) + (EMA_50 * 49 / 51)
		if EMA_20 > EMA_50:
			return 1 , 0
		else:
			return 0 , 1
	except:
		print("MA Cross error")




def VOLIT(formatted_data,oi):
	try:
		open_interest = goose.select_data_at_index(formatted_data, 7)
		open_interest = [float(i) for i in open_interest]
		open_interest.append(float(oi))
		open_interest = open_interest[-60:]
		volume = goose.select_data_at_index(formatted_data, 11)
		volume = [float(i) for i in volume]
		df = pd.DataFrame({'open_interest': open_interest, 'volume': volume})

		df["volume_ma"] = df["volume"].rolling(window=14).mean()
		df["open_interest_ma"] = df["open_interest"].rolling(window=14).mean()

		df["volume_ma1"] = df["volume"].rolling(window=1).mean()
		df["open_interest_ma1"] = df["open_interest"].rolling(window=1).mean()

		df["volume_roc"] = 100 * (df["volume"] - df["volume"].shift(1)) / df["volume"].shift(1)
		df["volume_roc1"] = 100 * (df["volume"] - df["volume"].shift(1)) / df["volume"].shift(1)

		# Calculate the rate of change (ROC) of open interest
		df["open_interest_roc"] = 100 * (df["open_interest"] - df["open_interest"].shift(1)) / df["open_interest"].shift(1)
		df["open_interest_roc1"] = 100 * (df["open_interest"] - df["open_interest"].shift(1)) / df["open_interest"].shift(1)

		df["custom_indicator"] = (df["volume_ma"] * 0.4) + (df["open_interest_ma"] * 0.3) + (df["volume_roc"] * 0.2) + (df["open_interest_roc"] * 0.1)
		df["custom_indicator_no_average"] = (df["volume_ma1"] * 0.4) + (df["open_interest_ma1"] * 0.3) + (df["volume_roc1"] * 0.2) + (df["open_interest_roc1"] * 0.1)

		df["custom_indicator_std"] = df["custom_indicator"].rolling(window=14).std()
		df["custom_indicator_std1"] = df["custom_indicator_no_average"].rolling(window=14).std()

		df["normalized_custom_indicator"] = (df["custom_indicator"] - df["custom_indicator"].rolling(window=14).mean()) / df["custom_indicator_std"]
		df["normalized_custom_indicator1"] = (df["custom_indicator_no_average"] - df["custom_indicator_no_average"].rolling(window=14).mean()) / df["custom_indicator_std1"]


		return df["normalized_custom_indicator"].iloc[-1], df["custom_indicator"].iloc[-1], df["custom_indicator_no_average"].iloc[-1], df["normalized_custom_indicator1"].iloc[-1]	
	except Exception as e:
		print(e)
		print("VOLIT error")


def find_support_resistance(formatted_data, lookback, p):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(p))
		support = []
		resistance = []
		for i in range(0+lookback, len(price)-1-lookback):
			if price[i] == min(price[i-lookback:i+lookback+1]):
				support.append(price[i])
			if price[i] == max(price[i-lookback:i+lookback+1]):
				resistance.append(price[i])
		#return 3 support and resistance levels (if they exist) if not set to 0
		if len(resistance) > 3:
			resistance = resistance[-3:]
		else:
			resistance = resistance + [0] * (3 - len(resistance))
		if len(support) > 3:
			support = support[-3:]
		else:
			support = support + [0] * (3 - len(support))

		return support[0], support[1], support[2], resistance[0], resistance[1], resistance[2]
	except Exception as e:
		print(e)
		print("Support Resistance error")

def Weighted_MA(formatted_data, lookback, p):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(p))
		weighted_ma = 0
		for i in range(0+lookback, len(price)-1-lookback):
			weighted_ma += price[i] * (lookback - i)
		weighted_ma = weighted_ma / (lookback * (lookback + 1) / 2)
		return weighted_ma
	except Exception as e:
		print(e)
		print("Weighted MA error")

def True_strength_index(formatted_data, lookback, p):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(p))
		#Calculate the average gain and loss over the lookback period
		gain = 0
		loss = 0
		for i in range(0+lookback, len(price)-1-lookback):
			if price[i] > price[i-1]:
				gain += price[i] - price[i-1]
			else:
				loss += price[i-1] - price[i]
		gain = gain / lookback
		loss = loss / lookback
		#Calculate the true strength index
		tsi = 100 * gain / (gain + loss)
		return tsi
	except Exception as e:
		print(e)
		print("TSI error")

def Stochastic_RSI(formatted_data, lookback):
	try:
		RSI = goose.select_data_at_index(formatted_data,18)
		RSI = [float(i) for i in RSI]
		RSI_latest = RSI[-lookback:]
		RSI_min = min(RSI_latest)
		RSI_max = max(RSI_latest)
		stochastic_RSI = (RSI[-1] - RSI_min) / (RSI_max - RSI_min)
		return stochastic_RSI
	except Exception as e:
		print(e)
		print("Stochastic RSI error")

		


def Percentage_Volume_Oscillator(formatted_data, lookback, p):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(p))
		#Calculate the average gain and loss over the lookback period
		volume = goose.select_data_at_index(formatted_data, 5)
		volume = [float(i) for i in volume]
		volume.append(float(p))
		#Calculate the average gain and loss over the lookback period
		gain = 0
		loss = 0
		for i in range(0+lookback, len(price)-1-lookback):
			if price[i] > price[i-1]:
				gain += volume[i]
			else:
				loss += volume[i]
		gain = gain / lookback
		loss = loss / lookback
		#Calculate the true strength index
		pvo = 100 * (gain - loss) / (gain + loss)
		return pvo
	except Exception as e:
		print(e)
		print("PVO error")

def Accumulation_Distribution(formatted_data, lookback):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		#Calculate the average gain and loss over the lookback period
		volume = goose.select_data_at_index(formatted_data, 11)
		volume = [float(i) for i in volume]
		#Calculate the average gain and loss over the lookback period
		acc_dist = 0
		for i in range(0+lookback, len(price)-1-lookback):
			acc_dist += volume[i] * ((price[i] - min(price[i-lookback:i+lookback+1])) - (max(price[i-lookback:i+lookback+1]) - price[i])) / (max(price[i-lookback:i+lookback+1]) - min(price[i-lookback:i+lookback+1]))
		acc_dist = acc_dist / lookback
		return acc_dist
	except Exception as e:
		print(e)
		print("Accumulation Distribution error")


def Donchian_Channels(formatted_data, lookback, p):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(p))
		#Calculate the average gain and loss over the lookback period
		upper = max(price[len(price)-lookback-1:len(price)-1])
		lower = min(price[len(price)-lookback-1:len(price)-1])
		middle = (upper + lower) / 2
		return upper, lower , middle
	except Exception as e:
		print(e)
		print("Donchian Channels error")

def Ulcer_Index(formatted_data, lookback, p):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		price.append(float(p))
		#Calculate the average gain and loss over the lookback period
		avg = sum(price[len(price)-lookback-1:len(price)-1]) / lookback
		ulcer = 0
		for i in range(0+lookback, len(price)-1-lookback):
			ulcer += (price[i] - avg) ** 2
		ulcer = (ulcer / lookback) ** 0.5
		return ulcer
	except Exception as e:
		print(e)
		print("Ulcer Index error")


def Volume_price_Trend(formatted_data, lookback):
	try:
		price = goose.select_data_at_index(formatted_data, 1)
		price = [float(i) for i in price]
		#Calculate the average gain and loss over the lookback period
		volume = goose.select_data_at_index(formatted_data, 11)
		volume = [float(i) for i in volume]
		#Calculate the average gain and loss over the lookback period
		vpt = 0
		for i in range(0+lookback, len(price)-1-lookback):
			vpt += volume[i] * (price[i] - price[i-1])
		vpt = vpt / lookback
		return vpt
	except Exception as e:
		print(e)
		print("Volume Price Trend error")


def get_data(index):
	try:
		client = bybit.bybit(test=False,api_key="FwnzUmI53zrJNQErck",api_secret="oXFqQ4dnxeKBx8ghdhwBMdc1AAtNLHeg3wlM")
		info = client.Market.Market_symbolInfo().result()
		keys = info[0]["result"]
		btc = keys[index]
		price = btc["last_price"]
		prev24_price = btc["prev_price_24h"]
		try:
			percent = (int(float(price)) - int(float(prev24_price))) / int(float(prev24_price)) * 100
		except:
			percent = 0
		high_24h = btc["high_price_24h"]
		low_24h = btc["low_price_24h"]
		prev1_price = btc["prev_price_1h"]
		open_interest = btc["open_interest"]
		turnover24 = btc["turnover_24h"]
		volume24 = btc["volume_24h"]
		funding_rate = btc["funding_rate"]
		current_time = time.time()
		
		temp = [current_time, price , prev24_price, percent, high_24h, low_24h, prev1_price, open_interest, turnover24, volume24, funding_rate]
		labels = ["time", "price" , "prev24_price", "percent", "high_24h", "low_24h", "prev1_price", "open_interest", "turnover24", "volume24", "funding_rate"]
		data = [str_to_round(value) for value in temp]
		df = pd.DataFrame([data], columns=labels)

		data = get_logs()
		data_index = {"time": 0, "price" : 1, "prev24_price": 2, "percent": 3, "high_24h": 4, "low_24h": 5, "prev1_price": 6, "open_interest": 7, "turnover24": 8, "volume24": 9, "funding_rate": 10}

		Volume_var = Volume(data)
		df["Volume"] = Volume_var
		average_volume_var = average_volume(data)
		average_price_var = average_price(data,price)
		average_direction_var = average_direction(data,price)
		POC_var = POC(data)
		TPO_var = TPO(data,price)
		VWAP_var = VWAP(data)
		RSI_var = RSI(data,price)
		MACD_var = MACD(data,price)
		OBV_var = OBV(data)
		band1, band2, band3 = boulanger_bands(data,price)
		r1 , r2 , r3 , s1 , s2 , s3 = find_support_resistance(data, 5, price)
		v1, v2 , v3 , v4 = VOLIT(data,open_interest)
		ct1 , ct2 , ct3 = change_of_trend(data,price)
		p1 , p2 , p3 = price_pattern(data,price)
		mc1 , mc2 = MA_cross(data,price)
		Weighted_MA_var1 = Weighted_MA(data, 5, price)
		Weighted_MA_var2 = Weighted_MA(data, 10, price)
		Weighted_MA_var3 = Weighted_MA(data, 20, price)
		True_strength_index1 = True_strength_index(data, 5, price)
		True_strength_index2 = True_strength_index(data, 10, price)
		True_strength_index3 = True_strength_index(data, 20, price)
		Percentage_Volume_Oscillator1 = Percentage_Volume_Oscillator(data, 5, price)
		Percentage_Volume_Oscillator2 = Percentage_Volume_Oscillator(data, 10, price)
		Percentage_Volume_Oscillator3 = Percentage_Volume_Oscillator(data, 20, price)
		Stochastic_RSI1 = Stochastic_RSI(data, 5)
		Stochastic_RSI2 = Stochastic_RSI(data, 10)
		Stochastic_RSI3 = Stochastic_RSI(data, 20)
		Accumulation_Distribution1 = Accumulation_Distribution(data, 5)
		Accumulation_Distribution2 = Accumulation_Distribution(data, 10)
		Accumulation_Distribution3 = Accumulation_Distribution(data, 20)
		dc1 , dc2 , dc3  = Donchian_Channels(data, 5, price)
		dc4 , dc5 , dc6  = Donchian_Channels(data, 10, price)
		dc7 , dc8 , dc9  = Donchian_Channels(data, 20, price)
		Ulcer_Index1 = Ulcer_Index(data, 5, price)
		Ulcer_Index2 = Ulcer_Index(data, 10, price)
		Ulcer_Index3 = Ulcer_Index(data, 20, price)
		Volume_price_Trend1 = Volume_price_Trend(data, 5)
		Volume_price_Trend2 = Volume_price_Trend(data, 10)
		Volume_price_Trend3 = Volume_price_Trend(data, 20)




		df["average_volume"] = average_volume_var
		df["average_price"] = average_price_var
		df["average_direction"] = average_direction_var
		df["POC"] = POC_var
		df["TPO"] = TPO_var
		df["VWAP"] = VWAP_var
		df["RSI"] = RSI_var
		df["MACD"] = MACD_var
		df["OBV"] = OBV_var
		df["Boulanger Band1"] = band1
		df["Boulanger Band2"] = band2
		df["Boulanger Band3"] = band3
		df["Resistance1"] = r1
		df["Resistance2"] = r2
		df["Resistance3"] = r3
		df["Support1"] = s1
		df["Support2"] = s2
		df["Support3"] = s3
		df["VOLIT1"] = v1
		df["VOLIT2"] = v2
		df["VOLIT3"] = v3
		df["VOLIT4"] = v4
		df["Change of Trend1"] = ct1
		df["Change of Trend2"] = ct2
		df["Change of Trend3"] = ct3
		df["Price Pattern1"] = p1
		df["Price Pattern2"] = p2
		df["Price Pattern3"] = p3
		df["MA Cross1"] = mc1
		df["MA Cross2"] = mc2
		df["Weighted MA1"] = Weighted_MA_var1
		df["Weighted MA2"] = Weighted_MA_var2
		df["Weighted MA3"] = Weighted_MA_var3
		df["True Strength Index1"] = True_strength_index1
		df["True Strength Index2"] = True_strength_index2
		df["True Strength Index3"] = True_strength_index3
		df["Percentage Volume Oscillator1"] = Percentage_Volume_Oscillator1
		df["Percentage Volume Oscillator2"] = Percentage_Volume_Oscillator2
		df["Percentage Volume Oscillator3"] = Percentage_Volume_Oscillator3
		df["Stochastic RSI1"] = Stochastic_RSI1
		df["Stochastic RSI2"] = Stochastic_RSI2
		df["Stochastic RSI3"] = Stochastic_RSI3
		df["Accumulation Distribution1"] = Accumulation_Distribution1
		df["Accumulation Distribution2"] = Accumulation_Distribution2
		df["Accumulation Distribution3"] = Accumulation_Distribution3
		df["Donchian Channel1"] = dc1
		df["Donchian Channel2"] = dc2
		df["Donchian Channel3"] = dc3
		df["Donchian Channel4"] = dc4
		df["Donchian Channel5"] = dc5
		df["Donchian Channel6"] = dc6
		df["Donchian Channel7"] = dc7
		df["Donchian Channel8"] = dc8
		df["Donchian Channel9"] = dc9
		df["Ulcer Index1"] = Ulcer_Index1
		df["Ulcer Index2"] = Ulcer_Index2
		df["Ulcer Index3"] = Ulcer_Index3
		df["Volume price Trend1"] = Volume_price_Trend1
		df["Volume price Trend2"] = Volume_price_Trend2
		df["Volume price Trend3"] = Volume_price_Trend3




		#boulanger band signal
		if float(price) > float(df["Boulanger Band1"]):
			df["Boulanger Band Signal1"] = 1 
			df["Boulanger Band Signal2"] = 0
			df["Boulanger Band Signal3"] = 0
		elif float(price) < float(df["Boulanger Band3"]):
			df["Boulanger Band Signal1"] = 0 
			df["Boulanger Band Signal2"] = 0
			df["Boulanger Band Signal3"] = 1
		else:
			df["Boulanger Band Signal1"] = 0
			df["Boulanger Band Signal2"] = 1
			df["Boulanger Band Signal3"] = 0

		def close_to_level(level , area = 2.5):
			if float(price) > float(level) - area and float(price) < float(level) + area:
				return True
			else:
				return False
		
		#support resistance signal
		if close_to_level(df["Resistance1"]):
			df["Support Resistance Signal1"] = 1
		else:
			df["Support Resistance Signal1"] = 0
		if close_to_level(df["Resistance2"]):
			df["Support Resistance Signal2"] = 1
		else:
			df["Support Resistance Signal2"] = 0
		if close_to_level(df["Resistance3"]):
			df["Support Resistance Signal3"] = 1
		else:
			df["Support Resistance Signal3"] = 0
		if close_to_level(df["Support1"]):
			df["Support Resistance Signal1"] = 1
		else:
			df["Support Resistance Signal1"] = 0
		if close_to_level(df["Support2"]):
			df["Support Resistance Signal2"] = 1
		else:
			df["Support Resistance Signal2"] = 0
		if close_to_level(df["Support3"]):
			df["Support Resistance Signal3"] = 1
		else:
			df["Support Resistance Signal3"] = 0
		

		print(df)

		return df
	except Exception as e:
		print("Error",e)
		log_error(str(e))

result_lock = threading.Lock()
results = []

def get_balance(account_info):
    balance = API.get_balance(account_info[1], account_info[2], account_info[3])
    with result_lock:
        results.append((account_info, balance))

def load_all_accounts():
    database = sql.connect("database.db")
    cursor = database.cursor()
    
    accounts = cursor.execute("SELECT * FROM accounts").fetchall()
    
    threads = []
    for account in accounts:
        thread = threading.Thread(target=get_balance, args=(account,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    DB = app.DB()
 
    for account_info, balance in results:
        print(f"Account {account_info[0]} - Balance: {balance}")
        DB.add_balance(account_info[0], balance[1] , balance[0])

    

def run(index):
	while True:
		try:
			start = time.time()
			index = find_btc()
			df = get_data(index)
			df = pd.DataFrame(df)
			df.to_csv("bybit-upgrade.csv", mode="a", header=False)
			load_all_accounts()
			print("Data saved")
			# try:
			# 	direction , price = page_backend.bot_predict()
			# 	print("Bot predicted")
			# except Exception as e:
			# 	print("Error",e)
			# 	log_error(e)
			# try:
			# 	page_backend.edit_page(direction, price)
			# 	print("Page updated")
			# except Exception as e:
			# 	print("Error",e)
			# 	log_error(e)
			# try:
			# 	data_formating.main()
			# 	print("Data formatted")
			# except Exception as e:
			# 	print("Error",e)
			# 	log_error(e)
			# try:
			# 	page_backend.show_data()
			# 	print("Data shown")
			# except Exception as e:
			# 	print("Error",e)
			# 	log_error(e)
		except Exception as e:
			print("Error",e)
			log_error(str(e))
		try:
			time.sleep(60-(time.time()-start))
			print ("Loop completed")
		except Exception as e:
			print("Error",e)
			log_error(str(e))

def find_btc():
	try:
		client = bybit.bybit(test=False,api_key="FwnzUmI53zrJNQErck",api_secret="oXFqQ4dnxeKBx8ghdhwBMdc1AAtNLHeg3wlM")
		info = client.Market.Market_symbolInfo().result()
		keys = info[0]["result"]
		for index , key in enumerate(keys):
			if key["symbol"].lower().startswith("btcusd"):
				return index
	except Exception as e:
		print("Error",e)
		log_error(str(e))

		

# if __name__ == "__main__":
# 	index = find_btc()
# 	run(index)

# load_all_accounts()

