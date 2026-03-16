"""
    제작 시간 : 0316_15:24
    유형 : 예제
    주제 : 
    문제 설명 : 
    - 
"""

# 기본 모듈
import sys



def main() -> None:
    books = [
        {
            "제목" : "혼자 공부하는 파이썬",
            "가격" : 24000
        },
        {
            "제목" : "혼자 공부하는 자바스크립트",
            "가격" : 21000
        },
        {
        "제목" : "혼자 공부하는 C언어",
        "가격" : 30000
        }
    ]
    
    def 가격함수추출(book):
        return book["가격"]
    
    print(" # 가장 저렴한 책")
    print(min(books, key = 가격함수추출))
    print()
    
    print(" # 가장 비싼 책")
    print(max(books, key = 가격함수추출))
    
    print(" # 람다식 사용 싼책, 비싼책6")
    print(min(books, key = lambda book:book["가격"]))
    print(max(books, key = lambda book:book["가격"]))

    print("# 가격 오름차순 정렬")
    books.sort(key = lambda book:book["가격"])
    for book in books:
        print(book)
    
    
    
    
    pass


if __name__ == "__main__":
    main()