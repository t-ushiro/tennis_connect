# streamlit run app.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import time
import streamlit as st
#test

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # ヘッドレスモード
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")  # 必要に応じて追加
    chrome_options.add_argument("--disable-dev-shm-usage")  # 必要に応じて追加
    
    # WebDriverのインストールと起動
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


# def click_button_by_id(driver, id=""):
#     try:
#         element = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, id))
#         )
#         driver.execute_script("arguments[0].click();", element)
#         return True
    
#     except Exception as e:
#         print("Error is occured:", e)
#         return False

# def click_button_by_xpath(driver, xpath=""):
#     try:
#         element = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, xpath))
#         )
#         print(f"element: {element}")
#         driver.execute_script("arguments[0].click();", element)
#         return True

#     except Exception as e:
#         print("Error is occured:", e)
#         return False
    
    
def click_element(driver, by=By.ID, selector="", wait_time=10, check_invisibility=False, invisibility_wait_time=3):
    """
    指定した方法（ID/Class/XPath）で要素を検索し、クリックする共通関数
    
    Args:
        driver: WebDriverインスタンス
        by: 要素の検索方法（By.ID, By.CLASS_NAME, By.XPATH）
        selector: 要素を特定するためのセレクタ文字列
        wait_time: 要素が表示されるまでの待機時間
        check_invisibility: クリック後に要素が消えたかを確認するかどうか
        invisibility_wait_time: 要素が消えるまでの待機時間
    
    Returns:
        bool: 操作が成功したかどうか
    """
    try:
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((by, selector))
        )
        print(f"element found: {element}")
        driver.execute_script("arguments[0].click();", element)
        
        if check_invisibility:
            try:
                WebDriverWait(driver, invisibility_wait_time).until(
                    EC.invisibility_of_element_located((by, selector))
                )
                print(f"要素が正常に消えました。selector: {selector}")
                return True
            except Exception as e:
                print(f"要素が消えていません。selector: {selector}")
                return False
        
        return True

    except Exception as e:
        print(f"Error occurred: {e}")
        return False

def click_load_more_button(driver, max_attempts=5):
    attempts = 0
    while attempts < max_attempts:
        try:
            # さらに読み込むボタンを待機
            load_more_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "btn.btn-quaternary"))
            )
            # ボタンが表示されていない場合は終了
            if not load_more_button.is_displayed():
                print("これ以上読み込むデータはありません")
                break
            # ボタンをクリック
            driver.execute_script("arguments[0].click();", load_more_button)
            print(f"さらに読み込むボタンをクリック: {attempts + 1}回目")
            attempts += 1

        except Exception as e:
            attempts += 1
            print("データが読み込めていないか、これ以上読み込むデータはありません（エラー発生）:", e)
            time.sleep(1)
            continue
    
    return attempts > 0


def input_date_by_id(driver, id, value):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, id))
        )
        element.clear()  # 既存の値をクリア
        element.send_keys(value)  # YYYY-MM-DD形式で日付を入力
        return True
    except Exception as e:
        print("Error is occured:", e)
        return False

def input_time_by_id(driver, id, value):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, id))
        )
        # 時間を4桁の文字列に変換（例: "10:00" → "1000"）
        time_value = value.replace(":", "")
        driver.execute_script(
            "arguments[0].value = arguments[1]; "
            "arguments[0].dispatchEvent(new Event('change'));", 
            element, time_value
        )
        return True
    except Exception as e:
        print("Error is occured:", e)
        return False




def get_facility_info(driver):
    """
    施設情報テーブルから情報を取得する関数
    
    Returns:
        list: 各施設の情報を辞書形式で格納したリスト
    """
    try:
        # テーブルが読み込まれるまで待機
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table.table.table-bordered.table-striped.facilities"))
        )
        
        # すべての行を取得
        rows = table.find_elements(By.TAG_NAME, "tr")
        facilities = []
        
        # ヘッダー行をスキップして2行目から処理
        for row in rows[1:]:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 5:  # 必要な列数があることを確認
                facility_info = {
                    "施設": cols[0].text,
                    "室場": cols[1].text,
                    "日付": cols[2].text,
                    "時間帯": cols[3].text
                }
                facilities.append(facility_info)
                print(f"取得した施設情報: {facility_info}")
        
        return facilities

    except Exception as e:
        print(f"施設情報の取得中にエラーが発生しました: {e}")
        return []


def main():
    try:
        # Chrome WebDriverのパスを指定してChromeブラウザを起動
        driver = webdriver.Chrome()

        # Webページにアクセス
        driver.get("https://www.shisetsu.city.yokohama.lg.jp/user/Home")
        
        # 室場の分類
        id = "__BVID__53___BV_tab_button__"
        result = click_element(driver, By.ID, selector=id)
        if not result:
            raise Exception(f"ボタンをクリックできませんでした。id: {id}")

        # 室場の種類
        xpath = "/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[1]/div[1]/div/div[1]/label"
        result = click_element(driver, By.XPATH, selector=xpath)
        if not result:
            raise Exception(f"ボタンをクリックできませんでした。xpath: {xpath}")

        # 利用目的の分類
        xpath ="/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[2]/div[1]/div/div[1]/label"
        result = click_element(driver, By.XPATH, selector=xpath)
        if not result:
            raise Exception(f"ボタンをクリックできませんでした。xpath: {xpath}")

        # 利用目的
        xpath = "/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[1]/div[3]/div/div[1]/label"
        result = click_element(driver, By.XPATH, selector=xpath)
        if not result:
            raise Exception(f"ボタンをクリックできませんでした。xpath: {xpath}")
        xpath ="/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[2]/div[3]/div/div[22]/label"
        result = click_element(driver, By.XPATH, selector=xpath)
        if not result:
            raise Exception(f"ボタンをクリックできませんでした。xpath: {xpath}")

        # 利用期間:開始日
        id = "HomeModel_DateFrom"
        result = input_date_by_id(driver, id, "2024-11-09")
        if not result:
            raise Exception(f"ボタンをクリックできませんでした。id: {id}")
        
        # 利用期間:終了日
        id = "HomeModel_DateTo"
        result = input_date_by_id(driver, id, "2024-11-13")
        if not result:
            raise Exception(f"ボタンをクリックできませんでした。id: {id}")
        
        # 利用時間: 開始時間
        id = "HomeModel_TimeFrom"
        result = input_time_by_id(driver, id, "10:00")
        if not result:
            raise Exception(f"ボタンをクリックできませんでした。id: {id}")

        # 利用時間: 終了時間
        id = "HomeModel_TimeTo"
        result = input_time_by_id(driver, id, "24:00")
        if not result:
            raise Exception(f"ボタンをクリックできませんでした。id: {id}")

        # 検索対象
        xpath = '/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[6]/div/div/div[1]/label'
        result = click_element(driver, By.XPATH, selector=xpath)
        if not result:
            raise Exception(f"ボタンをクリックできませんでした。xpath: {xpath}")

        # 検索ボタン
        xpath = '/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[7]/button'
        result = click_element(driver, By.XPATH, selector=xpath)
        if not result:
            print(f"ボタンをクリックできませんでした。xpath: {xpath}")

        # ポップアップの閉じるボタン
        class_name = "btn.btn-quaternary.btn-md"
        result = click_element(driver, By.CLASS_NAME, selector=class_name, check_invisibility=True)
        if not result:
            print(f"ボタンをクリックできませんでした。class_name: {class_name}")

        # さらに読み込むボタン
        result = click_load_more_button(driver)
        if not result:
            print("さらに読み込むボタンをクリックできませんでした。")
            # raise Exception("さらに読み込むボタンをクリックできませんでした。")

        facilities = get_facility_info(driver)
        print(f"取得した施設情報: {facilities}")
        # for facility in facilities:
        #     print(f"""
        #     施設: {facility['施設']}
        #     室場: {facility['室場']}
        #     日付: {facility['日付']}
        #     時間帯: {facility['時間帯']}
        #     ------------------------
        #     """)


    except Exception as e:
        print("Error is occured:", e)

    time.sleep(1000)
    driver.quit()





def app():
    st.title("横浜市施設予約システム 空き状況確認")
    
    # 日付入力
    col1, col2 = st.columns(2)
    with col1:
        target_date = st.date_input("利用日", value=None)
    
    # # 時間入力
    # col3, col4 = st.columns(2)
    # with col3:
    #     start_time = st.time_input("開始時間")
    # with col4:
    #     end_time = st.time_input("終了時間")
    
    if st.button("空き状況を確認"):
        driver = setup_driver()
        with st.spinner("データを取得中....."):
            try:
                
                
                # メインの処理を実行
                driver.get("https://www.shisetsu.city.yokohama.lg.jp/user/Home")
                
                # 日付と時間を適切な形式に変換
                formatted_date = target_date.strftime("%Y-%m-%d")
                
                container = st.empty()
                container.write(f"利用日: {formatted_date}で検索を開始します。")
                
                # 室場の分類
                id = "__BVID__53___BV_tab_button__"
                result = click_element(driver, By.ID, selector=id)
                if not result:
                    container.write("室場の分類を選択できませんでした。")
                    raise Exception(f"ボタンをクリックできませんでした。id: {id}")
                else:
                    container.write("室場の分類を選択しました！！") 
                    
                # 室場の種類
                xpath = "/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[1]/div[1]/div/div[1]/label"
                result = click_element(driver, By.XPATH, selector=xpath)
                if not result:
                    container.write("室場の種類を選択できませんでした。")
                    raise Exception(f"ボタンをクリックできませんでした。xpath: {xpath}")
                else:
                    container.write("室場の種類を選択しました！！") 

                # 利用目的の分類
                xpath ="/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[2]/div[1]/div/div[1]/label"
                result = click_element(driver, By.XPATH, selector=xpath)
                if not result:
                    container.write("利用目的の分類を選択できませんでした。")
                    raise Exception(f"ボタンをクリックできませんでした。xpath: {xpath}")
                else:
                    container.write("利用目的の分類を選択しました！！") 

                # 利用目的
                xpath = "/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[1]/div[3]/div/div[1]/label"
                result = click_element(driver, By.XPATH, selector=xpath)
                if not result:
                    container.write("利用目的を選択できませんでした。")
                    raise Exception(f"ボタンをクリックできませんでした。xpath: {xpath}")
                else:
                    container.write("利用目的を選択しました！！") 
                xpath ="/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[2]/div[3]/div/div[22]/label"
                result = click_element(driver, By.XPATH, selector=xpath)
                if not result:
                    container.write("利用目的を選択できませんでした。")
                    raise Exception(f"ボタンをクリックできませんでした。xpath: {xpath}")
                else:
                    container.write("利用目的を選択しました！！") 

                # 利用期間:開始日
                id = "HomeModel_DateFrom"
                result = input_date_by_id(driver, id, formatted_date)
                if not result:
                    container.write("利用期間の開始日を入力できませんでした。")
                    raise Exception(f"ボタンをクリックできませんでした。id: {id}")
                else:
                    container.write("利用期間の開始日を入力しました！！") 
                
                # 利用期間:終了日
                id = "HomeModel_DateTo"
                result = input_date_by_id(driver, id, formatted_date)
                if not result:
                    container.write("利用期間の終了日を入力できませんでした。")
                    raise Exception(f"ボタンをクリックできませんでした。id: {id}")
                else:
                    container.write("利用期間の終了日を入力しました！！") 
                
                # 利用時間: 開始時間
                id = "HomeModel_TimeFrom"
                result = input_time_by_id(driver, id, "10:00")
                if not result:
                    container.write("利用時間の開始時間を入力できませんでした。")
                    raise Exception(f"ボタンをクリックできませんでした。id: {id}")
                else:
                    container.write("利用時間の開始時間を入力しました！！") 

                # 利用時間: 終了時間
                id = "HomeModel_TimeTo"
                result = input_time_by_id(driver, id, "24:00")
                if not result:
                    container.write("利用時間の終了時間を入力できませんでした。")
                    raise Exception(f"ボタンをクリックできませんでした。id: {id}")
                else:
                    container.write("利用時間の終了時間を入力しました！！") 

                # 検索対象
                xpath = '/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[6]/div/div/div[1]/label'
                result = click_element(driver, By.XPATH, selector=xpath)
                if not result:
                    container.write("検索対象を選択できませんでした。")
                    raise Exception(f"ボタンをクリックできませんでした。xpath: {xpath}")
                else:
                    container.write("検索対象を選択しました！！") 

                # 検索ボタン
                xpath = '/html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div[1]/div/div[7]/button'
                result = click_element(driver, By.XPATH, selector=xpath)
                if not result:
                    container.write("検索ボタンをクリックできませんでした。")
                    raise Exception(f"ボタンをクリックできませんでした。xpath: {xpath}")
                else:
                    container.write("検索ボタンをクリック") 

                container.write("空きコートを検索中...")
                # ポップアップの閉じるボタン
                class_name = "btn.btn-quaternary.btn-md"
                result = click_element(driver, By.CLASS_NAME, selector=class_name, check_invisibility=True)
                if not result:
                    container.write("ポップアップの閉じるボタンをクリックできませんでした。")
                    print(f"ボタンをクリックできませんでした。class_name: {class_name}")
                else:
                    container.write("ポップアップの閉じるボタンをクリックしました！！") 

                # さらに読み込むボタン
                result = click_load_more_button(driver)
                if not result:
                    container.write("さらに読み込むボタンをクリックできませんでした。")
                    # raise Exception("さらに読み込むボタンをクリックできませんでした。")

                facilities = get_facility_info(driver)
                print(f"取得した施設情報: {facilities}")
                # for facility in facilities:
                #     print(f"""
                #     施設: {facility['施設']}
                #     室場: {facility['室場']}
                #     日付: {facility['日付']}
                #     時間帯: {facility['時間帯']}
                #     ------------------------
                #     """)
                
                container.empty()
                
                # 結果の表示
                if facilities:
                    st.success("データの取得に成功しました")
                    st.write("取得した施設情報:")
                    for facility in facilities:
                        if facility['施設'] is not None:
                            st.write(f"""
                            - 施設: {facility['施設']}
                            - 室場: {facility['室場']}
                            - 日付: {facility['日付']}
                            - 時間帯: {facility['時間帯']}
                            """)
                else:
                    st.warning("利用可能な施設が見つかりませんでした")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
            
            finally:
                driver.quit()

if __name__ == "__main__":
    app()