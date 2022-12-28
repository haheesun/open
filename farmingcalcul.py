#####종목검색############
import os
import sys

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *


class Kiwoom(QAxWidget):

    def __init__(self):
        super().__init__()

        self.realType = RealType()

        ####### event loop 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calcullator_event_loop = QEventLoop()
        ########################

        ######### 스크린 번호 모음
        self.screen_my_info = "2000"
        self.screen_calculation_stock = "4000"
        self.screen_real_stock = "5000" #종목별로 할당할 스크린 번호
        self.screen_meme_stock = "6000" #종목별 할당할 주문용 스크린 번호
        self.screen_start_stop_real = "1000"

        ############################

        ######## 변수모음
        self.account_num = None
        ########################

        ######### 계좌 관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5

        ######## 변수 모음
        self.portfolio_stock_dict = {}
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        self.jango_dict = {}
        self.meme_today_dict = {}
        self.meme_today_2_dict = {}
        self.rank_dict = {}
        self.no_stock_dict = {}
        self.base_price = {}

        #############################

        ######### 종목 분석용
        self.calcul_data = []
        ########################



        self.get_ocx_instance()
        self.event_slots()
        self.real_event_slots()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info() #예수금 가져오는 것
        self.detail_account_mystock()  #계좌평가 잔고내역 요청

        self.not_concluded_account() #미체결 요청

#####################TEST TEST###############################################
        self.read_code()  # 저장된 종목들 불러온다
        self.file_delete()
        self.calcullator_fnc() #종목분석용 임시
        # sys.exit()
###########################################################################

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)
        self.OnReceiveMsg.connect(self.msg_slot)


    def real_event_slots(self):
        self.OnReceiveRealData.connect(self.realdata_slot)
        self.OnReceiveChejanData.connect(self.chejan_slot)


    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_event_loop.exit()

    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCNO")

        self.account_num = account_list.split(';')[0]

        print("나의 계좌번호 %s" % self.account_num) #8155567311모의
        # slack.chat.post_message('#stock', "나의 계좌번호 %s" % self.account_num)

    def detail_account_info(self):

        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구문", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구문", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString))", "예수금상세현황요청","opw00001", "0", self.screen_my_info)

        self.detail_account_info_event_loop.exec_()


    def detail_account_mystock(self, sPrevNext="0"):

        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구문", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구문", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString))", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)


        self.detail_account_info_event_loop.exec_()



    def not_concluded_account(self, sPrevNext="0"):

        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.dynamicCall("CommRqData(QString, QString, int, QString))", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()


    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''
        TR요정을 받는 구역임 슬롯임
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청ID, TR코드
        :param sRecordName: 사용 안함
        :param sPrevNext: 다음 페이지가 있는지
        :return:
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금")

            print("예수금 %s" % int(deposit))


            self.use_money = int(deposit) * self.use_money_percent
            self.use_money = self.use_money / 2

            ok_deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
            print("출금가능금액 %s" % int(ok_deposit))

            self.detail_account_info_event_loop.exit()


        if sRQName == "계좌평가잔고내역요청":

            total_buy_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)

            print("총매입금액 %s" % total_buy_money_result)


            total_profit_loss_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)

            print("총수익률(%%) : %s" % total_profit_loss_rate_result)


            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                code = code.strip()[1:]

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code: {}})


                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt += 1


            print("현 계좌 보유 종목 %s" % self.account_stock_dict)
            print("현 계좌 보유종목 수 %s" % cnt)

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")

            else:
                self.detail_account_info_event_loop.exit()


        elif sRQName == "실시간미체결요청":

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)


            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태") #접수, 확인, 체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분") #-매도, +매수
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}

                nasd = self.not_account_stock_dict[order_no]

                nasd.update({"종목코드" : code})
                nasd.update({"종목명": code_nm})
                nasd.update({"주문번호": order_no})
                nasd.update({"주문상태": order_status})
                nasd.update({"주문수량": order_quantity})
                nasd.update({"주문가격": order_price})
                nasd.update({"주문구분": order_gubun})
                nasd.update({"미체결수량": not_quantity})
                nasd.update({"체결량": ok_quantity})

                print("미체결 종목 : %s" % self.not_account_stock_dict[order_no])
                # slack.chat.post_message('#stock', "미체결 종목 : %s" % self.not_account_stock_dict[order_no])

            self.detail_account_info_event_loop.exit()



        ###########################################################################################################
        if sRQName == "주식일봉차트조회":

            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("%s 일봉데이터 요청" % code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("데이터 일수 %s" % cnt)



            for i in range(cnt):
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())


            if sPrevNext == "0" or "2":
                print("총 일수 %s" % len(self.calcul_data))


                pass_success = False
######################################################################################################
##############################조건검색################################################################
#######################################################################################################

                if pass_success == True:
                    print("조건부 통과됨")

                    code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)

                    f = open("files/condition_farming.txt", "a", encoding="utf8") #a:이어쓴다, w:덮어쓴다
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()

                elif pass_success == False:
                    print("조건부 통과 못함")


                self.calcul_data.clear()
                self.calcullator_event_loop.exit()
                
######################################################################################################
##############################조건검색 끝################################################################
#######################################################################################################

    def get_code_list_by_market(self, market_code):
        '''
        종목 코드들 반환
        :param market_code:
        :return:
        '''
        market_list = [0]
        for market_code in market_list:
            code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
            code_list = code_list.split(";")[:-1]

        return code_list
    def get_code_list_by_market2(self, market_code2):
        '''
        종목 코드들 반환
        :param market_code:
        :return:
        '''
        market_list2 = [10]
        for market_code2 in market_list2:
            code_list2 = self.dynamicCall("GetCodeListByMarket(QString)", market_code2)
            code_list2 = code_list2.split(";")[:-1]

        return code_list2

        # 매수법칙 계산 들어가면 됨

    def read_code(self):
        if os.path.exists("files/condition_stock_no.txt"): #==true !=False
            f = open("files/condition_stock_no.txt", "r", encoding="utf8")

            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split("\t")

                    stock_code = ls[0]

                    self.no_stock_dict.update({stock_code:{}})

            f.close()

            print(self.no_stock_dict)


    def calcullator_fnc(self):
        '''
        종목 분석 실행용 함수
        :return:
        '''
        # time.sleep(25200)
        # time.sleep(30)

        code_list = self.get_code_list_by_market(0)
        code_list2 = self.get_code_list_by_market2(10)
        no_condition = self.read_code()
        for value in code_list2:
            code_list.append(value)


        print("검색대상 종목 갯수 %s" % len(code_list))


        for idx,code in enumerate(code_list):

            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)

            print("%s / %s : Stock Code : %s Stock is updating... " % (idx+1, len(code_list), code))

            self.day_kiwoom_db(code=code)





    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):

        QTest.qWait(3700) #3600은 타이트하게 가능

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)

        self.calcullator_event_loop.exec_()

    def realdata_slot(self, sCode, sRealType, sRealData):
        print("리얼")

    def chejan_slot(self, sGubun, nItemCnt, sFIdList):
        print("체잔")

    #송수신 메세지 get
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("스크린: %s, 요청이름: %s, tr코드: %s --- %s" %(sScrNo, sRQName, sTrCode, msg))

    #파일 삭제
    def file_delete(self):
        if os.path.isfile("files/condition_farming.txt"):
            os.remove("files/condition_farmingg.txt")



























