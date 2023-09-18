- 建立 lambda function
  - 啟用url
  - 建立layer
    - 製作zip
    ```bat
    conda create -n linebot python=3.9
    conda activate linebot
    pip install line-bot-sdk
    pip freeze > requirements.txt
    pip install -r requirements.txt -t ./python
    ```
      - 壓縮
    ```
  - 建立環境變數
    - LINE_CHANNEL_ACCESS_TOKEN
    - LINE_CHANNEL_SECRET
    - ACCESS_KEY
    - SECRET_KEY