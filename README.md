# 데이터베이스 학기 프로젝트


## 앱 응용의 목적
- 외부 공공데이터 기반 전국 축제 정보를 수집·정리해 목록/검색/상세/댓글 기능을 제공함.

## 데이터베이스의 구성
### 요구사항·설계·최종 스키마
- 요구사항: 축제 정보 목록/검색/조회/등록/수정/삭제, 댓글 작성/조회. 
- 설계 과정: 요구사항을 정리하고 간략하게 ERD 초안으로 축제/댓글 관계를 정의, 제약(FK, UNIQUE)과 인덱스 전략을 확인, 수집 흐름을 반영.
- 최종 스키마 생성
  - `Festival`: external_id, title, place, start_date, end_date, description, organizer, host, sponsor, telephone, homepage, extra_info, address_road, address_lot, latitude, longitude, data_reference_date, pub_date, created_at, updated_at
  - `Comment`: festival_id(FK), nickname, content, created_at
  - 제약/동작: `external_id` UNIQUE, `Festival.save`에서 title+start_date 중복 방지, FK cascade 삭제.
  - 최종 스키마 생성 코드
    ``` sql
      CREATE TABLE festivals_festival (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      external_id TEXT NOT NULL UNIQUE,
      title TEXT NOT NULL,
      place TEXT,
      start_date DATE,
      end_date DATE,
      description TEXT,
      organizer TEXT,
      host TEXT,
      sponsor TEXT,
      telephone TEXT,
      homepage TEXT,
      extra_info TEXT,
      address_road TEXT,
      address_lot TEXT,
      latitude REAL,
      longitude REAL,
      data_reference_date DATE,
      pub_date DATETIME,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- title + start_date 중복 방지
    CREATE UNIQUE INDEX ux_festival_external_id ON festivals_festival(external_id);
   
    CREATE UNIQUE INDEX ux_festival_title_start_date ON festivals_festival(title, start_date);

    CREATE TABLE festivals_comment (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      festival_id INTEGER NOT NULL,
      nickname TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(festival_id) REFERENCES festivals_festival(id) ON DELETE CASCADE
    );
    ```
## 사용하는 개발환경 (웹 프레임워크/언어/DBMS)
- 웹 프레임워크: Django 5.2.8 (Python 3.12)
- 언어: Python 3.12
- DBMS: SQLite 

## 데이터 출처
- CSV: 공공데이터포털 축제 데이터 다운로드 → `data.csv`저장 후 로드.
  - 출처를 첨부하려 했으나, 보고서 작성 당시 링크가 지워진 것으로 확인됨.
- 명령: `python manage.py load_festivals_from_csv --path data.csv`

## 서비스 동작과 페이지 스케치
- 축제 목록 보는 페이지
  - 축제 목록 확인 가능 (모든 사용자)
  - 축제 검색 가능 (모든 사용자)
  - 축제 추가 가능 (관리자로 접속한 경우)
- 축제 정보 페이지
  - 축제 정보 확인 가능 (모든 사용자)
  - 축제 댓글 작성 가능 (모든 사용자)
- 관리자 페이지 (관리자)
  - 축제 추가/삭제 가능
  - 댓글 삭제/추가 가능
  - 사용자 관리 가능

## 각 페이지의 DB 사용과 내부 SQL 개요
- 목록 페이지에서 검색어 “봄”으로 조회할 때
  ```sql
    SELECT id, title, place, start_date, end_date
    FROM festivals_festival
    WHERE title LIKE '%봄%'
    ORDER BY start_date, title
    LIMIT 12 OFFSET 0;
  ```
- 상세 페이지에서 축제(id=3) 클릭 시 축제 + 댓글 조회
    ```sql
    SELECT id, title, description, start_date, end_date
    FROM festivals_festival
    WHERE id = 3;
    SELECT id, nickname, content, created_at
    FROM festivals_comment
    WHERE festival_id = 3
    ORDER BY created_at DESC;
    ```
- 상세 페이지에서 댓글 작성(POST) “재밌겠어요”
    ```sql
    INSERT INTO festivals_comment (festival_id, nickname, content, created_at)
    VALUES (3, '재밌겠어요', CURRENT_TIMESTAMP);
    ```
- 관리자 생성 페이지에서 새 축제 등록(POST)
    ```sql
    INSERT INTO festivals_festival (external_id, title, place, start_date, end_date, pub_date)
    VALUES ('EXT-123', '봄꽃 축제', '서울', '2025-04-05', '2025-04-09', CURRENT_TIMESTAMP);
    ```
- 관리자 수정 페이지에서 축제 제목/장소 변경(POST)
    ```sql
    UPDATE festivals_festival
    SET title = '수정된 축제', place = '부산', updated_at = CURRENT_TIMESTAMP
    WHERE id = 3;
    ```
- 관리자 삭제 페이지에서 축제 삭제(POST) + FK CASCADE로 댓글도 삭제
  ```sql
  DELETE FROM festivals_festival
  WHERE id = 3;
  ```

## 실행/데이터 저장 메모
- `.env.example`를 복사해 `.env`에 API 키와 Django 설정을 채운다.
- 마이그레이션: `python manage.py migrate`
- 개발 서버: `python manage.py runserver`
- CSV 적재: `python manage.py load_festivals_from_csv --path data.csv`

## github에 소스코드 업로드한 주소
https://github.com/jjong102/Data-Base-Term-Project
