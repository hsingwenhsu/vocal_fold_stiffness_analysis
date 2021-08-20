# README

## 一些文件

- `report/`: 前跑的結果的pdf和excel檔案
- `New_data collection.xls`: 醫師的實驗結果和音檔選擇的資料
- `coa.13463.pdf`: 醫師的paper

## Data

- `raw_data/`: 
  - 包含醫生最初給的data的excel檔案, 還有轉成.csv的版本
  - 每一種音都有三個音檔, 檔名的最尾端會有: <唱名><編號>, e.g. `Do1`
  - 醫師給的原檔裡面, 聲波和壓力的data放在同一個column裡面用 "," 隔起來, 第一個位置是壓力(不是壓力差), 第二個位置的是聲波
- `cropped_data/`:
  - 包含醫師以前實驗的結果, data有經過裁剪
- `newdata/`: 醫師給的raw_data是壓力, 不是壓力差, 要得到醫師他們原本用的壓力差的話要對拿原始data跟醫師以前做過的實驗做一個matching, 這個資料夾裡面放的壓力差已經是matched過的了。另外醫師做實驗, 每一個音會有三份音檔, 只挑一份比較好的做, 這裡的檔案都已經挑完了, 所以檔名尾端都沒有分音檔編號, 只剩下唱名, 我自己把唱名全部改成小寫表示 e.g. `xxxx_mi.csv`
  - `pres/`: 壓力差的.csv檔
  - `freq/`: 聲波的.csv檔
  - `pres_ori/`: 原始壓力的.csv檔 (我的方法本身沒有使用這份資料, 但是畫圖做比較可以用)
- `newdata_cropped/`: 醫師做實驗只有用音檔裡一小段來做, 這是他們實驗時使用的那段的壓力差和聲波
  - `pres/`:壓力差的.csv檔
  - `freq/`:聲波的.csv檔

## Code 檔案結構

- 我嘗試了兩種方法, 一種是用Fourier transform, 找出聲波的頻率響應和基頻, 另一種是分析聲波amplitude和壓力差的關係
- 兩種方法都有一個資料夾, 裡面分別會有以下的檔案
  - `utils.py`: 包含一些讀檔的和兩種方法個別會需要的函示
  - `main.py`: 主要的程式, 會一次把三種音的結果都跑完
  - `makefile`: 裡面有把程式跑起來的指令

## `utils.py `裡面一些共同的functions

#### 讀檔

- `get_all_data(path, patient)`
  - Input: 儲存data的路徑 (e.g. `newdata/`)
  - Return: `f1, f2, f3, p1, p2, p3` (分別是so, do, mi的聲波和壓力差)
  - 以下的讀檔用function都包在這個function裏, 參考即可

- `get_data(filename)`
  - Input: `filename` 
  - Return: `data `(The column of a single csv file (我的csv檔案都只有一個column))
- `get_freq_names(path, patient)`
  - Input: 
    - `path`: 儲存frequency的路徑
    - `patient`: 病患的編號
  - Return:
    - `name1`, `name2`, `name3`: 分別是某病患的聲波的so, do, mi的檔名
- `get_pres_names(path, patient)`
  - Input:
    - `path`: 儲存pressure的路徑
    - `patient`: 病患的編號
  - Return: `name1`, `name2`, `name3`: 分別是某病患的壓力差的so, do, mi的檔名

#### Data Smoothing

- `get_smoothed_data(freq_data, pres_data, mf, note)`
  - 用途: 回傳有smoothed過的聲波和壓力, 下面的其他functions都包在這個function裡面
  - Input
    - `freq_data`: 聲波的訊號
    - `pres_data`: 壓力差的訊號
    - `mf`: 病患是男生或是女生 (`m`: 男, `f`: 女)
    - `note`: 唱名(e.g. `so` or  `do` or `mi`)

- `smooth_pres(data)`

  - 用途: 對壓力差做smoothing, 因為壓力差應該要是單調遞減, 只是會有少許波動, 所以有做smoothing
  - Input: `data`(壓力差的data)
  - Output: `smoothed_data`

- `smooth_freq(data, mf, note)`

  - 用途: 對聲波做smoothing, 因為每一種聲音的頻率都不一樣, 所以smoothing的window size會隨著不同的音和性別調整
  - Input: 
    - `data`: 聲波的data
    - `mf`: 病患是男生或是女生, 這個是用argv傳到程式裡的, e.g. `m` 代表男生, `f` 代表女生
    - `note`: 唱名的string, e.g. `so` 

  - Return: 
    - `smoothed_data`

## Method 1: Frequency (`frequency_final/`)

- 一共有兩個main(`main1.py`, `main2.py`), 分別是兩種方法, 兩個main共用一份makefile, 下不同的指令會跑不同份code

### `main1.py`

- `main1.py`用的方法是找correlation, correlation是指一個波和他之後的波的動態有某一種相關性, correlation最高的時候, 代表兩個波的動態有很高的相關
- 因為correlation需要比較多的波, 所以有時data太少的時候會在terminal裡面看到`if len segment < lag_thresh`的訊息, 出來的圖片會是空的

#### 流程

1. 讀檔
2. data smoothing
3. 利用correlation取得回歸線、頻率、壓力差
4. 做圖

#### Functions 說明

- `plot_correlation(freq_data, sp, path, patient, note, mf, cropped)`
  - 用途: 對freq_data做correlation, 函式裡面會產生一些圖片方便做比較跟檢查方法有沒有bug
  - Input
    - `freq_data`: 聲波的訊號, 沒有smoothed過
    - `sp`: smoothed壓力差
    - `patient`: 病患的編號
    - `note`: 唱名, e.g. `so` or `do` or `mi`
    - `mf`: 性別, e.g. `m` or `f`
    - `cropped`:使用沒有截過的data或是醫師之前使用的裁剪過的版本, (`'0' `代表沒裁減, `'1'`代表裁減)
  - Return
    - `rline`: 迴歸線的string, e.g. `y = ax+b`
    - `m`: 迴歸線的斜率
    - `tx`: 迴歸線的string在圖上x座標的位置
    - `ty`: 迴歸線的string在圖上y座標的位置
    - `poly1d_fn`: 迴歸線的函示, 帶入x座標的點會回傳y座標的結果
    - `freq`: 用correlation計算出來的週期倒數算出的frequency data points
    - `pres`: 對應每個週期的壓力差平均的data points

#### Makefile

- Makefile裡面有一區的指令是跑main1.py的:

  - 對沒有裁剪過的data跑`main1.py`

    ```
    $ make method1_0
    ```

  - 對有裁剪過的data跑`main1.py`

    ```
    $ make method1_1
    ```

#### Output

- 產生出來的圖片會存到`frequency_final/results/m`/或`frequency_final/results/f/`
- 檔案名稱說明(以病患編號`035_20190108-7`為例):
  - 未被裁減過的 data
    - `035_20190108-7_1_all.png`: 三個音合在一起的頻率對壓力差做圖
    - `035_20190108-7_1_slope.png`: 
    - `035_20190108-7_1_do_freq.png	`: 計算出來的頻率的data points做圖 (橫軸是data point的index)
    - `035_20190108-7_1_do_pres.png`: 對應頻率的壓力差的data points做圖 (橫軸是data point的index)
    - `035_20190108-7_1_do_result.png`: 單一一個音的頻率對壓力差做圖
    - `035_20190108-7_1_do.png`: 單一一個音correlation方法在聲波訊號上切出來的週期的圖
  - 裁減過的 data
    - `035_20190108-7_1_all_cropped.png`: 三個音合在一起的頻率對壓力差做圖
    - `035_20190108-7_1_do_cropped.png`: 單一一個音correlation方法在聲波訊號上切出來的週期的圖
    - ==註: 照理來說其實cropped的data足夠的話會產生出和沒有cropped的data一樣的一組照片, 但是通常點不夠只會有這兩種圖片, 如果三個音都失敗`patient_all_cropped.png`會是一張空的照片==

### `main2.py` 說明

- 方法二是用sliding window去擷取不同段的聲波訊號, 做Fourier transform找出該段聲音的主要的component, 照理來說是波動的週期有越多的話會越準, 但是男生的週期通常比較少, 尤其是低頻率的音, 所以window size會隨著性別跟音頻不太一樣

#### 流程

1. 讀檔
2. data smoothing
3. 計算window size
4. 擷取聲波和壓力差的segments
5. 傅立葉分析獲得頻率和每段segment平均的壓力差
6. 做圖

#### Functions 說明

- `plot_data2(out_path, patient, freq1, pres1, freq2, pres2, freq3, pres3, cropped, mf)`
  - 用途: 畫出結果
  - Input:
    - `out_path`:儲存結果的路徑
    - `patient`: 病患編號的string
    - `freq1`: so的聲音訊號
    - `pres1`: so的壓力差訊號
    - `freq2`: do的聲音訊號
    - `pres2`: do的壓力差訊號
    - `freq3`: mi的聲音訊號
    - `pres3`: mi的壓力差訊號

#### Makefile說明

- Makefile裡面有一區的指令是跑main2.py的:
  - 對沒有裁剪過的data跑`main2.py`

    ```
    $ make method2_0
    ```

  - 對有裁剪過的data跑`main2.py`

    ```
    $ make method2_1
    ```

#### Output

- 產生出來的圖片會存到`frequency_final/results/m`/或`frequency_final/results/f/`
- 檔案名稱說明(以病患編號`035_20190108-7`為例):
  - 未被裁減過的 data
    - `035_20190108-7_2_all.png`: 三個音合在一起的頻率對壓力差做圖
    - `035_20190108-7_2_do.png`: 單一一個音頻率對壓力差的做圖
    - `035_20190108-7_slope.png`: 斜率對頻率壓力差的做圖
  - 裁減過的 data
    - `035_20190108-7_2_all_cropped.png`: 三個音合在一起的頻率對壓力差做圖
    - `035_20190108-7_2_do_cropped.png`: 單一一個音頻率對壓力差的做圖
    - `035_20190108-7_slope_cropped.png`: 斜率對頻率壓力差的做圖

## Method 2: Amplitude (`amplitude_final/`)

- 經過和醫師討論之後覺得也許amplitude和壓力差會有更直接的關係, 所以這份code是用來找amplitude和壓力差的關係

### `utils.py` function說明

#### For Result

- `get_regression(amp, p)`
  - 用途: 輸入amplitude和壓力差的data points, 並且回傳迴歸線的一些information(用這些information做圖)
  - Input: 
    - `amp`: amplitude data points
    - `p`: 壓力差 data points
  - Return:
    - `rline`: 迴歸線的string, e.g. `y = ax+b`
    - `tx`: 迴歸線的string在圖上x座標的位置
    - `ty`：迴歸線的string在圖上y座標的位置
    - `poly1d_fn`: 迴歸線的函示, 帶入x座標的點會回傳y座標的結果
    - `m`: 迴歸線的斜率

### `main.py`說明

#### 流程

1. 讀檔
2. Data smoothing
3. 計算迴歸線資料
4. 做圖、存檔

#### `main.py`裡面的functions

- `find_amp(freq_data, pres_data, out_path, patient, note, cropped)`

  - 用途: 取聲波訊號的amplitude, 裡面有包含一些做圖的函示, 在聲波上點出波峰波谷的位置
  - Input:
    - `freq_data`:聲波訊號(smoothed)
    - `pres_data`:壓力差訊號(smoothed)
    - `out_path`:做圖的儲存路徑
    - `patient`:病患的編號
    - `note`:唱名
    - `cropped`:使用沒有截過的data或是醫師之前使用的裁剪過的版本, (`'0' `代表沒裁減, `'1'`代表裁減)
  - Return:
    - `amp_actual`: 振幅的data points
    - `pres_actual`: 振幅的data points對應的壓力差的data points

- `plot_data(out_path, patient, amps1, pres1, amps2, pres2, amps3, pres3, cropped)`

  - 用途: 將該病患的振幅-壓力差關係做圖、儲存

  - Input:

    - `out_path`: 儲存結果的路徑
    - `patient`: 病患編號
    - `amps1`: so的amplitude
    - `pres1`: so的pressure
    - `amps2`: do的amplitude
    - `pres2`: do的pressure
    - `amps3`: mi的amplitude
    - `pres3`: mi的pressure

    - `cropped`:使用沒有截過的data或是醫師之前使用的裁剪過的版本, (`'0' `代表沒裁減, `'1'`代表裁減)


#### Makefile

- 對未裁剪過的data跑程式:

  ```
  $ make amp
  ```

- 對裁剪過的data跑程式:

  ```
  $ make amp_cropped
  ```

  

### Output 說明

- Output的圖檔會存在`amplitude_final/results/`裡面, 下面有有兩個資料夾是`amplitude_final/results/m/`和`amplitude_final/results/f/`分別存男生跟女生的資料
- 各種output檔案名稱說明, 以下以patient `035_20190108-7`做說明
  - 未裁減data
    - `035_20190108-7_all.png`: 三個音合在一起的做圖 
    - `035_20190108-7_so_amp.png`: so單獨的做圖 
    - `035_20190108-7_do_amp.png`: do單獨的做圖 
    - `035_20190108-7_mi_amp.png`: mi單獨的做圖 
  - 裁減過的data
    - `035_20190108-7_all_cropped.png`: 三個音合在一起的做圖 
    - `035_20190108-7_so_amp_cropped.png`: so單獨的做圖 
    - `035_20190108-7_do_amp_cropped.png`: do單獨的做圖
    - `035_20190108-7_mi_amp_cropped.png`: mi單獨的做圖# vocal_fold_stiffness_analysis
