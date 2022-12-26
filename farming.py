########농사st매매##########

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

        self.buy_dict_1 = {}
        self.buy_dict_2 = {}
        self.addbuy_dict = {}
        self.addbuy_dict_2 = {}
        self.addbuy_dict_3 = {}

        self.acc_sell_dict_1 = {}
        self.acc_sell_dict_2 = {}

        self.sell_dict_end = {}

        self.start_dict_1 = {}
        self.start_dict_2 = {}
        self.tstart_dict_1 = {}
        self.tstart_dict_2 = {}

        self.not_meme_today_dict = {}

        self.sell_rebal = [0]
        self.sub_rebal = [0]
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

        # self.file_delete()
        # self.calcullator_fnc() #종목분석용 임시

###########################################################################
        self.read_code() #저장된 종목들 불러온다
        self.screen_number_setting() #스크린 번호를 할당


        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '', self.realType.REALTYPE['장시작시간']['장운영구분'], "0")

        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간']
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")
            print("실시간 등록 코드: %s, 스크린번호:%s, fid번호: %s" % (code, screen_num, fids))

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


    def detail_account_info(self):
        print("예수금 요청")


        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구문", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구문", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString))", "예수금상세현황요청","opw00001", "0", self.screen_my_info)

        self.detail_account_info_event_loop.exec_()


    def detail_account_mystock(self, sPrevNext="0"):
        print("계좌평가 잔고내역 요청하기 연속조회 %s" % sPrevNext)


        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구문", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구문", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString))", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)


        self.detail_account_info_event_loop.exec_()

    def not_concluded_account(self, sPrevNext="0"):
        print("미체결 요청")


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
                order_number = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태") #접수, 확인, 체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분") #-매도, +매수
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_number = int(order_number.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_number in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_number] = {}

                nasd = self.not_account_stock_dict[order_number]

                nasd.update({"종목코드": code})
                nasd.update({"종목명": code_nm})
                nasd.update({"주문번호": order_number})
                nasd.update({"주문상태": order_status})
                nasd.update({"주문수량": order_quantity})
                nasd.update({"주문가격": order_price})
                nasd.update({"주문구분": order_gubun})
                nasd.update({"미체결수량": not_quantity})
                nasd.update({"체결량": ok_quantity})

                print("미체결 종목 : %s" % self.not_account_stock_dict[order_number])


            self.detail_account_info_event_loop.exit()

        if sRQName == "주식일봉차트조회":

            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("%s 일봉데이터 요청" % code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("데이터 일수 %s" % cnt)


            #data = self.dynamicCall("GetCommData(QString, QString)", sTrCode, sRQName)
            #[['','현재가', '거래량', '거래대금', '날짜', '시가', '고가', '저가'. ''], ['','현재가', '거래량', '거래대금', '날짜', '시가', '고가', '저가'. '']]
            # 한번 조회하면 600일치까지 일봉데이터를 받을 수 있다.

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
            #     self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            #
            # else:

                # print("총 일수 %s" % len(self.calcul_data))

                pass_success = False

                #20일 이평선을 그릴만큼의 데이터가 있는지 체크
                if self.calcul_data == None or len(self.calcul_data) < 260:
                    pass_success = False

                else:

                    total_price = 0
                    for value in self.calcul_data[:20]: #[오늘, 하루전, ...19일전]
                        total_price += int(value[1])

                    moving_average_price = total_price / 20  #20일 이평선 만들어짐

                    #오늘자 주가가 20일 이평선 위에 있는지 확인
                    bottom_stock_price = False
                    check_price_1 = None
                    check_price_2 = None
                    check_price_3 = None
                    if int(self.calcul_data[0][7]) >= moving_average_price:

                        print("금일저가가 20이평선 위에 있음")
                        bottom_stock_price = True
                        check_price_1 = int(self.calcul_data[0][6])  # [5]금일고가
                        check_price_2 = int(self.calcul_data[0][1])  # [1]금일종가
                        check_price_3 = int(self.calcul_data[0][5])  # [5]금일시가


                        #전일 장대양봉 5%이상인지 확인
                    if bottom_stock_price == True:
                        pass_price = False

                        if (check_price_2 - check_price_3)/check_price_3 * 100 > 5 and 1000 < check_price_2 < 300000 and cnt > 265:
                                print("가격이 1000원과 300000원 내, 금일등락률 5%이상 장대양봉 포착")
                                pass_price = True

                    #과거 일봉들이 20일 이평선보다 위에 있는지 확인

                        if pass_price == True:


                            for i in range(1, 260):
                                if int(self.calcul_data[i][6]) - check_price_1 / check_price_1 > 5:
                                    print("%s일 전 금일고가보다 5%%이상 높은 %s원이 확인됨" % (i, int(self.calcul_data[i][1])))
                                    pass_success = False

                                    break
                                elif (i+10) > 260:
                                    print("52주 신고가 포착")
                                    pass_success = True
                                    break



                if pass_success == True:
                    print("조건부 통과됨")

                    code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)

                    f = open("files/condition_stock.txt", "a", encoding="utf8") #a:이어쓴다, w:덮어쓴다
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()



                elif pass_success == False:
                    print("조건부 통과 못함")


                self.calcul_data.clear()
                self.calcullator_event_loop.exit()



    # def get_code_list_by_market(self, market_code):
    #     '''
    #     종목 코드들 반환
    #     :param market_code:
    #     :return:
    #     '''
    #
    #     code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
    #     code_list = code_list.split(";")[:-1]
    #
    #     return code_list
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

    def calcullator_fnc(self):
        '''
        종목 분석 실행용 함수
        :return:
        '''
        # time.sleep(25200)
        # time.sleep(30)



        code_list = self.get_code_list_by_market(0)
        code_list2 = self.get_code_list_by_market2(10)
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

    #매수법칙 계산 들어가면 됨

    def read_code(self):
        if os.path.exists("files/condition_farming.txt"): #==true !=False
            f = open("files/condition_farming.txt", "r", encoding="utf8")

            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split("\t")

                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = int(ls[2])
                    stock_price = abs(stock_price)
                    start_price = int(ls[3])
                    start_price = abs(start_price)
                    end_price = int(ls[4].split("\n")[0])
                    end_price = abs(end_price)


                    self.portfolio_stock_dict.update({stock_code:{"종목명":stock_name, "현재가":stock_price, "장대시가":start_price, "장대종가":end_price}})

            f.close()

            print(self.portfolio_stock_dict)

    def screen_number_setting(self):

        screen_overwrite = []

        #계좌평가잔고내역에 있는 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #미체결에 있는 종목들
        for order_number in self.not_account_stock_dict.keys():
            code = self.not_account_stock_dict[order_number]['종목코드']

            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #포트폴리오에 담겨있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)


        #스크린번호 할당
        cnt = 0
        for code in screen_overwrite:

            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code: {"스크린번호":str(self.screen_real_stock), "주문용스크린번호": str(self.screen_meme_stock)}})

            cnt += 1
        print(self.portfolio_stock_dict)

    def realdata_slot(self, sCode, sRealType, sRealData):

        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)


            if value == '0':
                print("장 시작 전")
                # Next_Portfolio = False

            elif value == '3':
                print("장 시작")



            elif value == '2':
                print("장 종료, 동시호가로 넘어감")

            elif value == '4':
                print("장 종료")


                for code in self.portfolio_stock_dict.keys():
                    self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code)

                self.file_delete()
                sys.exit()

        if sRealType == "주식종목정보":
            z = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['증거금율표시']) # HHMMSS
            if sCode not in self.portfolio_stock_dict:
                self.portfolio_stock_dict.update({sCode: {}})

            psd = self.portfolio_stock_dict[sCode]

            psd.update({"증거금율표시": z})


            print(self.portfolio_stock_dict[sCode])

        if sRealType == "주식체결":
            a = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간']) # HHMMSS
            aa = int(a)

            b = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가'])  # +(-) 2500
            b = abs(int(b))

            c = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비'])  # 출력 : +(-)50
            c = int(c)

            d = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['등락율'])  # 출력 : +(-)12.98
            d = float(d)  #소수점이니깐

            e = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가'])  # 출력 : +(-)1000
            e = abs(int(e))

            f = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가'])  # 출력 : +(-)1000
            f = abs(int(f))

            g = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['거래량'])  # 출력 : 매도일떄: + 2024 매수일떄:- 2034
            g = int(g)

            h = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래량'])  # 출력 : 240124
            h = int(h)

            i = self.dynamicCall("GetCommRealData(QString, int)", sCode,  self.realType.REALTYPE[sRealType]['고가'])  # 출력 : +(-)2530
            i = abs(int(i))

            j = self.dynamicCall("GetCommRealData(QString, int)", sCode,  self.realType.REALTYPE[sRealType]['시가'])  # 출력 : +(-)2530
            j = abs(int(j))

            k = self.dynamicCall("GetCommRealData(QString, int)", sCode,  self.realType.REALTYPE[sRealType]['저가'])  # 출력 : +(-)2530
            k = abs(int(k))

            o = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결강도'])
            o = float(o)

            if sCode not in self.portfolio_stock_dict:
                self.portfolio_stock_dict.update({sCode: {}})

            psd = self.portfolio_stock_dict[sCode]

            psd.update({"체결시간": a})
            psd.update({"체결시간숫자": aa})
            psd.update({"현재가": b})
            psd.update({"전일대비": c})
            psd.update({"등락율": d})
            psd.update({"(최우선)매도호가": e})
            psd.update({"{최우선}매수호가": f})
            psd.update({"거래량": g})
            psd.update({"누적거래량": h})
            psd.update({"고가": i})
            psd.update({"시가": j})
            psd.update({"저가": k})
            psd.update({"체결강도": o})


            print(self.portfolio_stock_dict[sCode])


            # if sCode in self.jango_dict.keys() and sCode in self.buy_dict_1.keys():
            #     bd1 = self.buy_dict_1[sCode]
            #
            #     if bd1["매수후고가"] < b:
            #         bd1.update({"매수후고가": b})
            #
            # if sCode not in self.jango_dict.keys() and sCode in self.sell_dict_1_2.keys():
            #     sd1 = self.sell_dict_1_2[sCode]
            #
            #     if sd1["매도후저가"] > b:
            #         sd1.update({"매도후저가": b})


###################^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^##########################################
            ## 프로그램 조기 종료
            if aa > 152000:


                for code in self.portfolio_stock_dict.keys():
                    self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code)

                self.file_delete()
                sys.exit()

            money = 200000
            money1 = money + 10000
            money2 = (money * 2) + 10000



            newbuy_quan = int(money / b)
            addbuy_quan = newbuy_quan * 2

            # 계좌잔고평가내역에 있고 오늘 산 잔고에는 없을 경우

            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():

                asd = self.account_stock_dict[sCode]
                psd = self.portfolio_stock_dict[sCode]
                sell_half = int(asd['매매가능수량'] / 2) + 1 #보유금액의 절반
                meme_rate = ((b - asd['매입가']) / asd['매입가'] * 100) - 0.25 #수수료제외 수익률
                return_1 = (b - asd['매입가']) * sell_half
                return_e = (b - asd['매입가']) * asd['매매가능수량']

                if asd['매입금액'] < money1:
                    self.addbuy_dict.update({sCode: {}})
                if money1 <= asd['매입금액'] < money2:
                    self.addbuy_dict_2.update({sCode: {}})
                if money2 <= asd['매입금액']:
                    self.addbuy_dict_3.update({sCode: {}})

                if b + (b * 0.01) < psd['장대종가'] and sCode not in self.start_dict_1.keys():
                    self.start_dict_1.update({sCode: {}})
                if psd['장대종가'] <= b + (b * 0.01) and sCode not in self.start_dict_2.keys():
                    self.start_dict_2.update({sCode: {}})
            # 1차매도 ###############################################################################################################################
                if asd['매매가능수량'] > 0 and sCode not in self.acc_sell_dict_1.keys() and sCode in self.start_dict_1.keys():
                    # 장대종가 -1%에서 절반 매도
                    if b + (b * 0.01) >= psd['장대종가']:

                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                     ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                      sCode, sell_half, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_1.update({sCode:{}})
                        self.sell_rebal.append(return_1)
                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")

                    #장대종가대비 -5%에서 전량매도
                    elif sCode in self.addbuy_dict_2.keys() and meme_rate > 10 and sCode not in self.sell_dict_end.keys():

                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                     ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                      sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_1.update({sCode:{}})
                        self.sell_dict_end.update({sCode: {}})
                        self.sell_rebal.append(return_e)

                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")

                # 1차매도 리밸런스 ###############################################################################################################################
                if sCode not in self.acc_sell_dict_1.keys():
                    rebal = sum(self.sell_rebal) - sum(self.sub_rebal)
                    rebal_quan = rebal / b
                    psd_s = self.portfolio_stock_dict[sCode]['장대시가']

                    if (b - psd_s) / psd_s * 100 < -45 and asd['매매가능수량'] > 0 and len(self.addbuy_dict) > 0 and sCode in self.addbuy_dict_3.keys():


                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                         ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                          sCode, rebal_quan, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_1.update({sCode: {}})
                        return_r = (b - asd['매입가']) * rebal_quan
                        self.sub_rebal.append(return_r)

                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")



                    else:
                        self.acc_sell_dict_1.update({sCode: {}})

                        print("보유리벨패스")



                # 2차매도 ###############################################################################################################################
                # 2차매도 ###############################################################################################################################
                if asd['매매가능수량'] > 0 and sCode not in self.acc_sell_dict_2.keys() and sCode in self.start_dict_2.keys() and sCode not in self.sell_dict_end.keys():
                    #장대종가대비 +10%
                    if b - (b * 0.1) >= psd['장대종가']:

                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                         ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                          sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_2.update({sCode: {}})
                        self.sell_dict_end.update({sCode: {}})
                        self.sell_rebal.append(return_e)

                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")
                    #장대종가대비 -5% 전량익절
                    elif b + (b * 0.05) < psd['장대종가']:

                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                         ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                          sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_2.update({sCode: {}})
                        self.sell_dict_end.update({sCode: {}})
                        self.sell_rebal.append(return_e)

                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")


                # 2차매도 리밸런스 ###############################################################################################################################
                if sCode not in self.acc_sell_dict_2.keys():
                    psd_s = self.portfolio_stock_dict[sCode]['장대시가']

                    if (b - psd_s) / psd_s * 100 < -45 and asd['매매가능수량'] > 0 and len(self.addbuy_dict) > 0 and sCode in self.addbuy_dict_3.keys():

                        rebal = sum(self.sell_rebal) - sum(self.sub_rebal)
                        rebal_quan = rebal / b

                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                         ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                          sCode, rebal_quan, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_2.update({sCode: {}})
                        return_r = (b - asd['매입가']) * rebal_quan
                        self.sub_rebal.append(return_r)

                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")


                    else:
                        self.acc_sell_dict_2.update({sCode: {}})

                        print("보유리벨패스")

############### # 잔고평가내역에 있을 경우  ##########################


            elif sCode in self.jango_dict.keys():
                psd = self.portfolio_stock_dict[sCode]
                jd = self.jango_dict[sCode]
                sell_quanj = int(((jd['주문가능수량'] * b) - money) / b) #20만원 초과 금액분
                sell_halfj = int(jd['주문가능수량'] / 2) + 1 #보유금액 절반
                buy_quanj = int((money - (jd['주문가능수량'] * b)) / b) #20만원 부족 금액분
                meme_ratej = ((b - jd['매입단가']) / jd['매입단가'] * 100) - 0.25 #수수료 제외 수익률
                returnj_1 = (b - jd['매입단가']) * sell_halfj
                returnj_e = (b - jd['매입단가']) * jd['주문가능수량']

                if (b + (b * 0.01)) < psd['장대종가'] and sCode not in self.tstart_dict_1.keys():
                    self.tstart_dict_1.update({sCode: {}})
                if psd['장대종가'] <= (b + (b * 0.01)) and sCode not in self.tstart_dict_2.keys():
                    self.tstart_dict_2.update({sCode: {}})

#***************************************************************************************
                # 1차매도 ###############################################################################################################################
                if jd['주문가능수량'] > 0 and sCode not in self.acc_sell_dict_1.keys() and sCode in self.tstart_dict_1.keys():

                    if (b + (b * 0.01)) >= psd['장대종가']:

                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                         ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                          sCode, sell_halfj, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_1.update({sCode: {}})
                        self.sell_rebal.append(returnj_1)

                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")

                    elif sCode in self.addbuy_dict_2.keys() and meme_ratej > 10 and sCode not in self.sell_dict_end.keys():

                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                         ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                          sCode, jd['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_1.update({sCode: {}})
                        self.sell_dict_end.update({sCode: {}})
                        self.sell_rebal.append(returnj_1)

                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")

                # 1차매도 리밸런스 ###############################################################################################################################
                if sCode not in self.acc_sell_dict_1.keys() :
                    rebal = sum(self.sell_rebal) - sum(self.sub_rebal)
                    rebal_quan = rebal / b
                    psd_s = self.portfolio_stock_dict[sCode]['장대시가']

                    if jd['주문가능수량'] > 0 and (b - psd_s) / psd_s * 100 < -45 and len(self.addbuy_dict) > 0 and sCode in self.addbuy_dict_3.keys():

                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                         ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                          sCode, rebal_quan, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_1.update({sCode: {}})
                        return_r = (b - jd['매입단가']) * rebal_quan
                        self.sub_rebal.append(return_r)

                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")



                # 2차매도 ###############################################################################################################################
                # 2차매도 ###############################################################################################################################
                if jd['주문가능수량'] > 0 and sCode not in self.acc_sell_dict_2.keys() and sCode in self.tstart_dict_2.keys() and sCode not in self.sell_dict_end.keys():

                    if (b - (b * 0.1)) >= psd['장대종가']:

                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                         ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                          sCode, jd['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_2.update({sCode: {}})
                        self.sell_dict_end.update({sCode: {}})
                        self.sell_rebal.append(returnj_e)

                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")

                    elif (b + (b * 0.05)) < psd['장대종가']:

                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                         ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                          sCode, jd['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_2.update({sCode: {}})
                        self.sell_dict_end.update({sCode: {}})
                        self.sell_rebal.append(returnj_e)

                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")

                # 2차매도 리밸런스 ###############################################################################################################################
                if sCode not in self.acc_sell_dict_2.keys():
                    psd_s = self.portfolio_stock_dict[sCode]['장대시가']

                    if jd['주문가능수량'] > 0 and (b - psd_s) / psd_s * 100 < -45 and len(self.addbuy_dict) > 0 and sCode in self.addbuy_dict_3.keys():
                        rebal = sum(self.sell_rebal) - sum(self.sub_rebal)
                        rebal_quan = rebal / b

                        order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                         ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                          sCode, rebal_quan, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        self.acc_sell_dict_2.update({sCode: {}})
                        return_r = (b - jd['매입단가']) * rebal_quan
                        self.sub_rebal.append(return_r)

                        if order_success == 0:


                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")

                    else:
                        self.acc_sell_dict_2.update({sCode: {}})

                        print("잔고리벨패스")


############매수주문############################################^^^^^^^^^^^^^^^^^##########################################################################################################
            elif len(self.account_stock_dict) < 20:
                psd_s = self.portfolio_stock_dict[sCode]['장대시가']
                psd_e = self.portfolio_stock_dict[sCode]['장대종가']
                psd_t = ((psd_e - psd_s) / 4) + psd_s

                if (psd_t - (psd_t * 0.01)) < b < (psd_t + (psd_t * 0.01)) and sCode not in self.buy_dict_1.keys():

                    order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                     ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                                      sCode, newbuy_quan, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    self.buy_dict_1.update({sCode: {}})
                    if order_success == 0:

                        print("매수주문 전달 성공")

                    else:
                        print("매수주문 전달 실패")

            elif aa > 151000 and len(self.addbuy_dict_2) <= 7:
                psd_s = self.portfolio_stock_dict[sCode]['장대시가']

                asd = self.account_stock_dict[sCode]
                second = ((b - asd['매입가']) / asd['매입가'] * 100) - 0.25  # 수수료제외 수익률

                if (b - psd_s) / psd_s * 100 < -20 and j < b and sCode in self.addbuy_dict.keys() and sCode not in self.buy_dict_2.keys():

                    order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                     ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                                      sCode, newbuy_quan, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    self.buy_dict_2.update({sCode: {}})
                    if order_success == 0:

                        print("매수주문 전달 성공")

                    else:
                        print("매수주문 전달 실패")


                if (b - psd_s) / psd_s * 100 < -36 and j < b and sCode in self.addbuy_dict_2.keys()and sCode not in self.buy_dict_2.keys():

                    order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                     ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                                      sCode, addbuy_quan, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    self.buy_dict_2.update({sCode: {}})
                    if order_success == 0:

                        print("매수주문 전달 성공")

                    else:
                        print("매수주문 전달 실패")

            ####################매수취소 오류시 아래부분 주석처리####################################################################################

            not_meme_list = list(self.not_account_stock_dict)

            for order_number in not_meme_list:
                code = self.not_account_stock_dict[order_number]["종목코드"]
                meme_price = self.not_account_stock_dict[order_number]["주문가격"]
                not_quantity = self.not_account_stock_dict[order_number]["미체결수량"]
                order_gubun = self.not_account_stock_dict[order_number]["주문구분"]
                chegual_time = self.not_account_stock_dict[order_number]["주문/체결시간"]
                chegual_time1 = int(chegual_time)

                if order_gubun == "매수" and not_quantity > 0 and 90000 < aa and aa >= chegual_time1 + 1000 and order_number not in self.not_meme_today_dict.keys():
                    order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                     ["매수취소", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 3, code, 0, 0,
                                                      self.realType.SENDTYPE['거래구분']['지정가'], order_number])
                    self.not_meme_today_dict.update({order_number:{}})

                    if order_success == 0:
                        print("매수취소 전달 성공")

                    else:
                        print("매수취소 전달 실패")


#############################################################################################################
    def chejan_slot(self, sGubun, nItemCnt, sFIdList):

        if int(sGubun) == 0:
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()
            origin_order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['원주문번호'])  #출력 : defaluse :"000000"
            order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문번호']) #출력 : 0115061 마지막주문번호
            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문상태']) #출력: 접수, 확인, 체결
            order_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문수량']) #출력 : 3
            order_quan = int(order_quan)
            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문가격']) #출력: 21000
            order_price = int(order_price)
            not_chegual_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['미체결수량'])
            not_chegual_quan = int(not_chegual_quan)
            order_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문구분'])
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
            chegual_time_str = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간'])
            chegual_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가'])
            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price = int(chegual_price)

            chegual_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량'])
            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity = int(chegual_quantity)
            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['현재가'])
            current_price = abs(int(current_price))
            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))
            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))


            ###### 새로 들어온 주문이면 주문번호 할당
            if order_number not in self.not_account_stock_dict.keys():
                self.not_account_stock_dict.update({order_number:{}})

            self.not_account_stock_dict[order_number].update({"계좌번호": account_num})
            self.not_account_stock_dict[order_number].update({"종목코드": sCode})
            self.not_account_stock_dict[order_number].update({"주문번호": order_number})
            self.not_account_stock_dict[order_number].update({"종목명": stock_name})
            self.not_account_stock_dict[order_number].update({"주문상태": order_status})
            self.not_account_stock_dict[order_number].update({"주문수량": order_quan})
            self.not_account_stock_dict[order_number].update({"주문가격": order_price})
            self.not_account_stock_dict[order_number].update({"미체결수량": not_chegual_quan})
            self.not_account_stock_dict[order_number].update({"원주문번호": origin_order_number})
            self.not_account_stock_dict[order_number].update({"주문구분": order_gubun})
            self.not_account_stock_dict[order_number].update({"주문/체결시간": chegual_time_str})
            self.not_account_stock_dict[order_number].update({"체결가": chegual_price})
            self.not_account_stock_dict[order_number].update({"체결량": chegual_quantity})
            self.not_account_stock_dict[order_number].update({"현재가": current_price})
            self.not_account_stock_dict[order_number].update({"(최우선)매도호가": first_sell_price})
            self.not_account_stock_dict[order_number].update({"{(최우선}매수호가": first_buy_price})

            print(self.not_account_stock_dict)




        elif int(sGubun) == 1:

            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목코드'])[1:]

            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['현재가'])
            current_price = abs(int(current_price))

            stock_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)

            like_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)

            buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))

            total_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['총매입가'])
            total_buy_price = int(total_buy_price)

            meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매도/매수구분'])
            meme_gubun = self.realType.REALTYPE['매도/매수구분'][meme_gubun]

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode:{}})

            self.jango_dict[sCode].update({"계좌번호": account_num})
            self.jango_dict[sCode].update({"현재가": current_price})
            self.jango_dict[sCode].update({"종목코드": sCode})
            self.jango_dict[sCode].update({"종목명": stock_name})
            self.jango_dict[sCode].update({"보유수량": stock_quan})
            self.jango_dict[sCode].update({"주문가능수량": like_quan})
            self.jango_dict[sCode].update({"매입단가": buy_price})
            self.jango_dict[sCode].update({"총매입가": total_buy_price})
            self.jango_dict[sCode].update({"매도/매수구분": meme_gubun})
            self.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})
            # self.jango_dict[sCode].update({"최대수익률": 0})

            print(self.jango_dict)



            if stock_quan == 0:
                del self.jango_dict[sCode]
                # self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[sCode]['스크린번호'], sCode)


    #송수신 메세지 get
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("스크린: %s, 요청이름: %s, tr코드: %s --- %s" %(sScrNo, sRQName, sTrCode, msg))

    #파일 삭제
    def file_delete(self):
        if os.path.isfile("files/condition_stock.txt"):
            os.remove("files/condition_stock.txt")



























