import pandas as pd

def clease_data(data: pd.DataFrame):
    # 6자리 만들고 앞에 0을 붙인다.
    data.종목코드 = data.종목코드.map('{:06d}'.format)

    # 필요없는 column들은 제외해준다.
    data = data[['회사명', '종목코드', '업종', '주요제품']]

    # 한글로된 컬럼명을 영어로 바꿔준다.
    return data.rename(
        columns={
            '회사명': 'code_name', 
            '종목코드': 'code', 
            '업종': 'category',
            '주요제품': 'product',
        }
    )

# 불성실공시법인 가져오는 함수
def get_companies_insincerity():
    data = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=05', header=0)[0]

    return clease_data(data)

# 관리 종목을 가져오는 함수
def get_companies_managing():
    data = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=01', header=0)[0]  # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌

    return clease_data(data)

# 코넥스 종목을 가져오는 함수
def get_companies_konex():
    data = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=konexMkt',header=0)[0]  # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌

    return clease_data(data)

# 코스피 종목을 가져오는 함수
def get_companies_kospi():
    data = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=stockMkt',header=0)[0]  # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌

    return clease_data(data)

# 코스닥 종목을 가져오는 함수
def get_companies_kosdaq():
    data = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt',header=0)[0]  # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌

    return clease_data(data)

# 코스피, 코스닥, 코넥스 모든 정보를 가져오는 함수
def get_companies():
    data = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]  # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌

    return clease_data(data)
