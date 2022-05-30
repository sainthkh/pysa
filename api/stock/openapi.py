import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import logging.handlers
import time
import datetime
from pandas import DataFrame

formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
logger = logging.getLogger("crumbs")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

TR_REQ_TIME_INTERVAL = 0.2


class Openapi(QAxWidget):
    def __init__(self):
        print("openapi __name__:", __name__)
        super().__init__()
        self._create_open_api_instance()
        self._set_signal_slots()
        self.comm_connect()
        self.account_info()
        self.first_600 = False

    def _opt10081(self, rqname, trcode):
        # 몇번 반복 실행 할지 설정
        ohlcv_cnt = self._get_repeat_cnt(trcode, rqname)

        # 하나의 row씩 append
        for i in range(ohlcv_cnt):
            date = self._get_comm_data(trcode, rqname, i, "일자")
            open = self._get_comm_data(trcode, rqname, i, "시가")
            high = self._get_comm_data(trcode, rqname, i, "고가")
            low = self._get_comm_data(trcode, rqname, i, "저가")
            close = self._get_comm_data(trcode, rqname, i, "현재가")
            volume = self._get_comm_data(trcode, rqname, i, "거래량")

            self.ohlcv.append({
                'date': date, 
                'open': int(open), 
                'high': int(high), 
                'low': int(low), 
                'close': int(close),
                'volume': int(volume),
            })

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        # print("_receive_tr_data!!!")
        # print(rqname, trcode, next)
        if self.first_600 and next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt10081_req":
            self._opt10081(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    # get_total_data : 특정 종목의 일자별 거래 데이터 조회 함수

    # 사용방법
    # code: 종목코드(ex. '005930' )
    # start : 기준일자. (ex. '20200424') => 20200424 일자 까지의 모든 open, high, low, close, volume 데이터 출력
    def _get_total_data(self, code, start):
        self.ohlcv = []
        self.set_input_value("종목코드", code)
        self.set_input_value("기준일자", start)
        self.set_input_value("수정주가구분", 1)
        self.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

        # 이 밑에는 한번만 가져오는게 아니고 싹다 가져오는거다.

        while self.remained_data == True:
            # time.sleep(TR_REQ_TIME_INTERVAL)
            self.set_input_value("종목코드", code)
            self.set_input_value("기준일자", start)
            self.set_input_value("수정주가구분", 1)
            self.comm_rq_data("opt10081_req", "opt10081", 2, "0101")

        time.sleep(0.2)

        return self.ohlcv
    
    def get_total_data(self, code: str, year: int, month: int, day: int):
        d = datetime.datetime(year, month, day)

        return self._get_total_data(code, d.strftime('%Y%m%d'))

    def get_first_600_days(self, code, date):
        self.first_600 = True
        self.ohlcv = [] #  {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}
        
        self.set_input_value("종목코드", code)
        self.set_input_value("기준일자", date)
        self.set_input_value("수정주가구분", 1)
        self.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

        time.sleep(0.2)

        return self.ohlcv

    def account_info(self):
        account_number = self.get_login_info("ACCNO")
        self.account_number = account_number.split(';')[0]
        logger.debug("계좌번호: " + self.account_number)

    def get_login_info(self, tag):
        try:
            ret = self.dynamicCall("GetLoginInfo(QString)", tag)
            time.sleep(TR_REQ_TIME_INTERVAL)
            return ret
        except Exception as e:
            logger.critical(e)

    def _create_open_api_instance(self):
        try:
            self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        except Exception as e:
            logger.critical(e)

    def _set_signal_slots(self):
        try:
            self.OnEventConnect.connect(self._event_connect)
            self.OnReceiveTrData.connect(self._receive_tr_data)
            self.OnReceiveMsg.connect(self._receive_msg)

        except Exception as e:
            is_64bits = sys.maxsize > 2**32
            if is_64bits:
                logger.critical('32bit 환경으로 실행하여 주시기 바랍니다.')
            else:
                logger.critical(e)

    def comm_connect(self):
        try:
            self.dynamicCall("CommConnect()")
            time.sleep(TR_REQ_TIME_INTERVAL)
            self.login_event_loop = QEventLoop()
            self.login_event_loop.exec_()
        except Exception as e:
            logger.critical(e)

    def _receive_msg(self, sScrNo, sRQName, sTrCode, sMsg):
        print(sMsg)

    def _event_connect(self, err_code):
        try:
            if err_code == 0:
                logger.debug("connected")
            else:
                logger.debug(f"disconnected. err_code : {err_code}")
            self.login_event_loop.exit()
        except Exception as e:
            logger.critical(e)

    def set_input_value(self, id, value):
        try:
            self.dynamicCall("SetInputValue(QString, QString)", id, value)
        except Exception as e:
            logger.critical(e)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        time.sleep(TR_REQ_TIME_INTERVAL)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _get_comm_data(self, code, field_name, index, item_name):
        ret = self.dynamicCall("GetCommData(QString, QString, int, QString)", code, field_name, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        try:
            ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
            return ret
        except Exception as e:
            logger.critical(e)

app = None

def init_openapi():
    global app

    app = QApplication(sys.argv)
    return Openapi()
