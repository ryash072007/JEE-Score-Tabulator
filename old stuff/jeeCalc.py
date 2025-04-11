class GetQAns:
    def __init__(self, QPat, APat):
        self.QPat = QPat
        self.APat = APat
    
    def GetQA(self, path = 'old stuff/data/AnswerKey.aspx.html'):
        data = []
        with open(path) as AnsKey:
            for line in AnsKey.readlines():
                if "QuestionNo" in line:
                    greaterThanPos = line.find('>')
                    lessThanPos = line.find('</')
                    Q = line[greaterThanPos+1:lessThanPos]
                    data.append([Q.strip()[-3:]])
                if "lbl_RAnswer" in line:
                    greaterThanPos = line.find('>')
                    lessThanPos = line.find('</')
                    A = line[greaterThanPos+1:lessThanPos]
                    data[-1].append(A.strip()[-3:])
        return data
    
    def ApplyPattern(self, datas):
        for i in range(len(datas)):
            if i in range(20, 25) or i in range(45, 50) or i in range(70, 75):
                datas[i][0] = str(abs(self.QPat + int(datas[i][0])))[-3:]
                datas[i][1] = datas[i][1]
            else:
                datas[i][0] = str(abs(self.QPat + int(datas[i][0])))[-3:]
                datas[i][1] = str(abs(self.APat + int(datas[i][1])))[-3:]

    def GetYourQA(self, path = 'data/ZZ13100308_2083O24372S14D756E1.html'):
        data = []
        with open(path) as AnsKey:
            QNext = False
            ANext = False
            IDNext = False
            NONMCQ = False
            nonmcqQNext = False
            for line in AnsKey.readlines():
                if "Question ID :" in line:
                    QNext = True
                    continue
                if QNext:
                    QNext = False
                    greaterThanPos = line.find('>')
                    lessThanPos = line.find('</')
                    if nonmcqQNext:
                        nonmcqQNext = False
                        A = line[greaterThanPos+1:lessThanPos]
                        data[-1].insert(0, A.strip()[-3:])
                        continue
                    else:
                        A = line[greaterThanPos+1:lessThanPos]
                        data.append([A.strip()[-3:]])
                if "Chosen Option :" in line:
                    ANext = True
                    continue
                if "Given Answer :" in line:
                    NONMCQ = True
                    continue
                if NONMCQ:
                    NONMCQ = False
                    greaterThanPos = line.find('>')
                    lessThanPos = line.find('</')
                    A = line[greaterThanPos+1:lessThanPos]
                    data.append([A.strip()[-3:]])
                    continue
                if '<td class="bold">SA</td>' in line:
                    nonmcqQNext = True
                    continue
                if ANext:
                    ANext = False
                    greaterThanPos = line.find('>')
                    lessThanPos = line.find('</')
                    A = line[greaterThanPos+1:lessThanPos]
                    data[-1].append(A.strip()[-3:])
                if "Option 1 ID :" in line:
                    IDNext = True
                    data[-1].append([])
                    continue
                if  "Option 2 ID :" in line or "Option 3 ID :" in line or "Option 4 ID :" in line:
                    IDNext = True
                    continue
                if IDNext:
                    IDNext = False
                    greaterThanPos = line.find('>')
                    lessThanPos = line.find('</')
                    A = line[greaterThanPos+1:lessThanPos]
                    data[-1][-1].append(A.strip()[-3:])

        return data

    def CheckAns(self, QA, YourQA):
        skipped = 0
        correct = 0
        incorrect = 0
        outputs = []
        for yourans_i in range(len(YourQA)):
            yourans = YourQA[yourans_i]
            ans = None

            for anses in QA:
                # print(yourans[0], anses[0])
                if yourans[0] == anses[0]:
                    ans = anses
                    break
            else:
                # print(f"error at Q: {yourans_i + 1}")
                outputs.append(f"error at Q: {yourans_i + 1}")
                continue

            if len(yourans) == 2:
                if yourans[1] == "--":
                    skipped += 1
                    outputs.append(f"Q{yourans_i + 1} (ID: {yourans[0]}): Skipped")
                    continue
                if yourans[1] == ans[1]:
                    outputs.append(f"Q{yourans_i + 1} (ID: {yourans[0]}): Correct (Answer ID: {ans[1]}, Chosen: {yourans[1]})")
                    correct += 1
                else:
                    outputs.append(f"Q{yourans_i + 1} (ID: {yourans[0]}): Incorrect (Answer ID: {ans[1]}, Chosen: {yourans[1]})")
                    incorrect += 1
            elif len(yourans) == 3:
                if yourans[2] == "--":
                    skipped += 1
                    outputs.append(f"Q{yourans_i + 1} (ID: {yourans[0]}): Skipped")
                    continue
                chosen_ans = str(int(yourans[1][int(yourans[2]) - 1]))
                if chosen_ans == ans[1]:
                    outputs.append(f"Q{yourans_i + 1} (ID: {yourans[0]}): Correct (Answer ID: {ans[1]}, Chosen: {chosen_ans})")
                    correct += 1
                else:
                    outputs.append(f"Q{yourans_i + 1} (ID: {yourans[0]}): Incorrect (Answer ID: {ans[1]}, Chosen: {chosen_ans})")
                    incorrect += 1
            else:
                outputs.append(f"error at Q: {yourans_i + 1}")
        print(f"Correct: {correct}, Incorrect: {incorrect}, Skipped: {skipped}")
        print(f"Score: {correct * 4 - incorrect}")
        return outputs
    
    def subjectWise(self, output):
        mathC = 0
        mathI = 0
        phyC = 0
        phyI = 0
        chemC = 0
        chemI = 0
        for i in range(25):
            if "Correct" in output[i]:
                mathC += 1
            if "Incorrect" in output[i]:
                mathI += 1
        
        for i in range(25, 50):
            if "Correct" in output[i]:
                phyC += 1
            if "Incorrect" in output[i]:
                phyI += 1
        
        for i in range(50, 75):
            if "Correct" in output[i]:
                chemC += 1
            if "Incorrect" in output[i]:
                chemI += 1
        
        print(f"Maths: Correct: {mathC}, Incorrect: {mathI}")
        print(f"Physics: Correct: {phyC}, Incorrect: {phyI}")
        print(f"Chemistry: Correct: {chemC}, Incorrect: {chemI}")

ans = GetQAns(56, -265) #Yash 28s2
# ans = GetQAns(0, 0) #Yash 28s2
# ans = GetQAns(225, -235) #Parth 23s1
# ans = GetQAns(-250, -450) #24s2
# ans = GetQAns(-250, -450)
# ans = GetQAns(756, 715) # 29s2
QA = ans.GetQA()
# print(QA)
print("____")
ans.ApplyPattern(QA)
yourqa = ans.GetYourQA("old stuff/data/ZZ13100308_2083O24372S14D756E1.html")
print(yourqa)

data = ans.CheckAns(QA, yourqa)
for i in data:
    print(i)

ans.subjectWise(data)

