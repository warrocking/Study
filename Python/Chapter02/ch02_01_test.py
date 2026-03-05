# p.100 문자열 생성

print("글자")
print('글자')
print("""문자열
문자열
문자열""")

# p.100 이스케이프 문자

print("큰 따움표 : \"")
print('작은 따움표 : \'')
print("역슬래쉬 : \\")
print("줄바꿈 : \n")
print("탭 : \t")

# 추가 문제
date = '20191025'
year = date[0:4]
month = date[4:6]
day = date[6:]
date2 = year + "년" + month + "월" + day + "일"
print(date2)