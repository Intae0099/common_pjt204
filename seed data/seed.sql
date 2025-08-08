describe admin;
describe application;
describe application_tag;
describe appointment;
describe client;
describe lawyer;
describe lawyer_tag;
describe participant;
describe refresh_token;
describe room;
describe session;
describe tag;
describe unavailability_slot;

select * from admin;
select * from application;
select * from application_tag;
select * from appointment;
select * from client;
select * from lawyer;
select * from lawyer_tag;
select * from participant;
select * from refresh_token;
select * from room;
select * from session;
select * from tag;
select * from unavailability_slot;

-- -----------------------------------------

select * from admin;
insert into admin (id, login_email, name, password_hash)
	values (1, 'admin@admin.com', '제갈관리', '$2a$10$6URHDdX68Pdv3RGIgOnToeviWRZrPrmxDXJplaUj/bQIsxkxbnHwu');

-- -----------------------------------------

select * from client;
insert into client (id, oauth_name, oauth_provider, email, oauth_identifier)
	values
		(1, '김태인', 'kakao', 'test11@test.com', '4365887081'),
        (2, '이정연', 'kakao', 'wjddusdl921@naver.com', '4381478225'),
        (3, '윤규성', 'kakao', 'gyuseong217@gmail.com', '4361466099'),
        (4, '권자은', 'kakao', 'pizzayumnum@gmail.com', '4384090851'),
        (5, '김도연', 'kakao', 'dodolove127@naver.com', '4365887021'),
        (6, '이준혁', 'kakao', 'jjunLee@edu.hanbat.ac.kr', '4365887965'),
        (7, '박서현', 'kakao', 's2park@naver.com', '4365887152'),
        (8, '최민재', 'kakao', 'jae981205@gmail.com', '4365887784'),
        (9, '한지훈', 'kakao', 'jh5656@kakao.com', '4365887365'),
        (10, '정하윤', 'kakao', null, '4365887845');

-- -----------------------------------------

select * from lawyer;
insert into lawyer (id, login_email, login_password_hash, name, introduction, photo, exam, registration_number, certification_status, consultation_count)
	values
		(1, 'songws81@hanmail.net', '$2a$10$g2NI1R0CvjK0MEe7eVHfdelmyHtoAtngTpO80NqPRZd2Hdp7yCB1e', '송우석', '대한민국의 주권은 국민에게 있고, 모든 권력은 국민으로부터 나온다! 권력에 맞서 싸우겠습니다.', null, '사법시험', '1981', 'APPROVED', 801),
        (2, 'taein918@hanmail.net', '$2a$10$aRxKGbYZrjofb2JRD5r5P.1yQVq1rOUr1oO0AcW97PhrrC8m0GXT2', '김태인', '최선을 다해 변호하겠습니다! 믿고 맡겨주세요.', null, '사법시험', '6521', 'APPROVED', 120),
        (3, 'zinzi9999@gmail.com', '$2a$10$Nll0dDJ8T4HZ1pexk.p9xujkGPqtugz6cXmSqk3MbiBVBCdqwmhBq', '황시목', '법은 날카로운 칼날과 같습니다. 감정은 배제하고 철저한 사실에 근거하여 변호하겠습니다.', null, '사법시험', '7988', 'APPROVED', 413),
        (4, 'hyeseong221@naver.com', '$2a$10$rrMuSD6IeQ7nbGzjJBXIKe07i2AZhyjUzbR2UU.gBJW4n0e8M2V/G', '장혜성', '국선 변호사 출신으로서, 진정성있는 변호를 보여드리겠습니다.', null, '사법시험', '8452', 'APPROVED', 201),
        (5, 'wooyeongwooS2@gmail.com', '$2a$10$lF4isyX60vVco.KyiafLNeitstkiEqAHLZ18ka/GNaLBRS4Jg87ZK', '우영우', '돌고래가 보여요! 천재 변호사 우영우입니다🐳', null, '로스쿨', '15320', 'APPROVED', 512),
        (6, 'eungyeong.biz@gmail.com', '$2a$10$L8Ofrts091l4OraRqS4dGu3hcezBd6zPz80HYJTMrVtKya.v9qu/a', '차은경', '이혼사건은 저에게 맡겨주세요. 감사합니다.^^', null, '로스쿨', '10224', 'APPROVED', 451);

-- -----------------------------------------

select * from tag order by id;
insert into tag (name)
values
    ('음주운전'),
    ('무면허운전'),
    ('성범죄'),
    ('마약사건'),
    ('폭력·폭행'),
    ('사기'),
    ('교통사고'),
    ('자동차손해배상'),
    ('보험합의'),
    ('이혼'),
    ('상간소송'),
    ('위자료'),
    ('재산분할'),
    ('양육권'),
    ('채무불이행'),
    ('계약분쟁'),
    ('소비자분쟁'),
    ('전세사기'),
    ('파산·회생'),
    ('개인회생'),
    ('채무조정'),
    ('상속·유류분'),
    ('유언검인'),
    ('상속재산분할'),
    ('특허'),
    ('상표'),
    ('저작권'),
    ('지적재산권'),
    ('부당해고'),
    ('근로기준법 위반'),
    ('산업재해'),
    ('노동법'),
    ('행정소송'),
    ('조세·세금'),
    ('병영법'),
    ('공정거래'),
    ('의료사고'),
    ('식품·의약품'),
    ('생명윤리'),
    ('개인정보보호'),
    ('환경오염'),
    ('건설·부동산'),
    ('소비자보호'),
    ('금융사기'),
    ('증권범죄'),
    ('기업파산'),
    ('M&A'),
    ('기업법무');

-- -----------------------------------------

select * from lawyer_tag;
insert into lawyer_tag (id, lawyer_id, tag_id)
values
	(1, 1, 12),
    (2, 1, 29),
    (3, 1, 30),
    (4, 1, 31),
    (5, 1, 32),
    (6, 1, 34),
    (7, 2, 13),
    (8, 2, 15),
    (9, 2, 19),
    (10, 2, 20),
    (11, 2, 21),
    (12, 2, 24),
    (13, 2, 29),
    (14, 2, 30),
    (15, 2, 32),
    (16, 3, 3),
    (17, 3, 4),
    (18, 3, 5),
    (19, 3, 7),
    (20, 3, 8),
    (21, 3, 12),
    (22, 4, 6),
    (23, 4, 13),
    (24, 4, 18),
    (25, 4, 22),
    (26, 4, 23),
    (27, 4, 24),
    (28, 4, 44),
    (29, 5, 3),
    (30, 5, 7),
    (31, 5, 8),
    (32, 5, 9),
    (33, 5, 12),
    (34, 6, 10),
    (35, 6, 11),
    (36, 6, 12),
    (37, 6, 13),
    (38, 6, 14),
    (39, 6, 23),
    (40, 6, 24);
    
-- -----------------------------------------
    
select * from application;
insert into application (id, client_id, is_completed, created_at, title, summary, content, outcome, disadvantage, recommended_question)
	values
		(1, 1, 1, '2025-08-01 10:25:00', '헬스장에서 실수로 여자 탈의실에 들어갔다가 고소당한 사건', '남자 탈의실인 줄 알고 여자 탈의실에 들어갔다가 여성 이용자에게 고소당한 사건입니다.', '운동을 마치고 탈의실에 가려고 했는데, 헷갈려서 여자 탈의실에 들어갔습니다. 안에 사람이 있는 줄 몰랐고, 몇 걸음 들어갔다가 바로 나왔는데도 여성 이용자분이 고소하셨습니다. 고의가 아니었고 불필요한 행동은 전혀 없었습니다.', '고소가 취하되거나 형사처벌 없이 사건이 마무리되길 원합니다. 합의가 가능하다면 원만히 해결하고 싶습니다.', '탈의실 안으로 들어간 사실은 CCTV에도 남아 있고, 피해자가 불쾌감을 느낀 건 사실입니다. 진술에서 ‘실수’라는 점을 설득력 있게 보여줄 수 있을지 걱정됩니다.', '{"question1" : "고의성이 없더라도 처벌받을 수 있나요?", "question2" : "피해자와 합의하면 형사처벌을 피할 수 있나요?", "question3" : "벌금형 외에 다른 처벌 가능성도 있나요?"}'),
        (2, 2, 1, '2025-08-02 09:17:52', '회사 비품(볼펜) 무단 반출로 횡령 고소당한 사건', '회사 볼펜 두 자루를 집에 가져간 것이 횡령으로 고소된 상황입니다.', '퇴근하면서 평소에 쓰던 볼펜 두 자루를 무심코 가방에 넣고 집에 가져갔습니다. 중요한 물건도 아니고 다음날 다시 가져다줄 생각이었습니다. 그런데 사장님이 CCTV를 확인하고 고의적인 절도 및 횡령이라고 주장하며 법적 조치를 하겠다고 했습니다.', '처벌을 피하고 회사와 원만하게 마무리하고 싶습니다. 다시 다니기 어렵겠지만 전과는 남기고 싶지 않습니다.', '퇴근 시간 이후였고, 평소에 개인적으로 쓰던 물건은 아니라 사적으로 가져간 것으로 보일 수 있습니다. 회사가 고소를 강하게 밀어붙이고 있어 합의가 어려울 것 같다는 점도 걱정입니다.', '{"question1" : "이 정도 사안도 횡령죄로 처벌될 수 있나요?", "question2" : "사장님이 고소를 취소하지 않으면 어떻게 되나요?", "question3" : "합의 없이 벌금형 정도로 끝낼 수 있을까요?"}'),
        (3, 3, 1, '2025-08-03 11:36:17', '퇴직 전 산업재해 인정 거부와 부당한 해고 통보', '10년 넘게 근무한 회사에서 허리디스크 산재신청을 하자마자 일방적으로 해고 통보를 받았습니다.', '저는 A전기설비업체에서 11년간 근무한 전기 기술자입니다. 약 1년 전, 공사 현장에서 무거운 자재를 운반하던 중 허리 통증이 악화되어 병원 진단 결과 디스크 판정을 받았습니다. 병원에서는 반복적 과중노동에 의한 산업재해로 의심된다고 했고, 산재 신청을 진행하였습니다. 하지만 회사는 제 질병이 개인 건강 문제라며 산재 신청을 막으려 했고, 최근에는 ‘업무 부적응’을 이유로 일방적인 해고를 통보받았습니다. 급여도 일부가 체불된 상태입니다.', '산업재해로 인정받고, 해고가 무효임을 주장하여 원직 복직 또는 부당해고 위자료를 받고 싶습니다.', '산재 신청 당시 개인적으로 허리 치료를 받았던 병원이 있어서, 회사 측이 이를 근거로 개인질병이라고 주장할 가능성이 있습니다. 정식 산재 인정보다 먼저 사적으로 치료받은 것이 불리하게 작용할까 걱정입니다.', '{"question1" : "산재로 인정받기 위해 필요한 입증 자료는 무엇인가요?", "question2" : "회사가 부당해고를 했다는 걸 증명할 수 있는 방법은?", "question3" : "해고 이후 체불된 임금과 위자료를 함께 청구할 수 있나요?"}'),
        (4, 4, 1, '2025-08-04 12:45:18', '성격차이로 인한 이혼 상담 요청', '배우자와의 지속적인 갈등으로 이혼을 원하고 있으며, 아이의 양육권과 재산 분할에 대해 상담을 요청합니다.', '결혼한 지 7년 되었고, 아이가 하나 있습니다. 배우자와는 생활방식과 가치관이 너무 달라서 매일 다툼이 이어지고 있습니다. 폭력이나 외도는 없지만 정서적으로 너무 지쳐서 이혼을 결심했습니다. 아이 양육권은 제가 갖고 싶고, 재산 분할에 있어 불리하지 않게 정리하고 싶습니다.', '협의이혼이든 재판이혼이든 최대한 빠르게 이혼하고, 자녀 양육권을 확보하고 싶습니다. 재산 분할도 공정하게 하고 싶습니다.', '상대방이 이혼에 동의하지 않고, 아이에 대한 애정이 깊어 양육권 문제로 강하게 다툴 가능성이 큽니다. 저는 소득이 상대방보다 적어서 양육권 분쟁에서 불리할까 걱정됩니다.', '{"question1" : "성격차이만으로 이혼이 가능할까요?", "question2" : "양육권을 확보하려면 어떤 점을 입증해야 하나요?", "question3" : "재산 분할에서 불리하지 않으려면 어떤 준비가 필요할까요?"}'),
        (5, 5, 1, '2025-08-04 16:22:01', '아버지 사망 후 상속재산 분할 문제로 형제와 갈등이 있습니다', '부친이 돌아가신 후 상속재산 분할을 두고 형제 간 갈등이 커지고 있어 법적 절차를 고민 중입니다.', '최근 부친이 유언 없이 돌아가셨고, 남겨진 재산은 시가 약 5억 원의 아파트와 예금 1억 정도입니다. 저는 막내이고, 다른 형제들이 이미 재산을 일부 사용하고 있는 정황이 있습니다. 상속재산 분할을 공정하게 받고 싶습니다.', '법정 지분에 따라 정당한 상속분을 확보하고 싶습니다.', '유족 간 감정싸움이 격해져 협의가 사실상 불가능하며, 제가 부모님 부양을 많이 했다는 부분은 입증자료가 부족합니다.', '{"question1" : "상속재산분할청구 소송을 바로 제기해도 되나요?", "question2" : "부양 기여분 주장 시 필요한 자료는 무엇인가요?", "question3" : "다른 형제가 재산을 임의로 처분한 경우 대응 방법은?"}'),
        (6, 6, 0, '2025-08-05 14:52:12', '제2금융권 대출로 인한 과다 채무', '소득이 없는 상태에서 다수의 대출로 인해 연체가 발생했고, 신용불량자가 되었습니다. 파산이나 회생 절차가 가능한지 궁금합니다.', '일시적인 수입으로 생활비와 치료비를 충당하기 위해 제2금융권 대출을 이용했는데, 현재 총 채무가 5천만 원 이상이고 연체가 3개월 넘었습니다. 소득은 거의 없으며 가족에게도 경제적 지원을 받기 어렵습니다.', null, null, null),
        (7, 7, 0, '2025-08-05 19:47:59', '편의점 아르바이트 임금 체불 문제', '2개월간 주말 아르바이트를 했는데, 마지막 급여 50만 원이 지급되지 않고 있습니다.', '편의점에서 주말 아르바이트를 했고, 처음 6주는 매주 급여를 받았지만, 마지막 두 주 급여는 매출이 안 좋다는 이유로 지급이 지연되고 있습니다. 고용주는 책임을 회피하고 있어 대응이 어렵습니다.', null, null, null),
        (8, 8, 0, '2025-08-06 13:26:13', '오토바이 교통사고 피해자 보험사 배상', '횡단보도에서 신호 대기 중이던 오토바이에 탑승 중, 뒤에서 차량이 추돌해 입원했으나 보험사 합의금이 턱없이 낮습니다.', '오토바이 뒤에 타고 있던 중 차량이 추돌하여 저는 허리 디스크 진단을 받고 5주 치료를 받았습니다. 가해 차량 보험사에서 제시한 합의금은 150만 원에 불과해, 치료비와 손해에 비해 너무 적다고 느낍니다.', null, null, null),
        (9, 9, 0, '2025-08-07 18:17:52', '택배 마약 운반 혐의', '해외 지인이 보낸 물건을 대신 받아주었는데, 그 안에 마약이 들어있어 마약 운반 혐의로 조사를 받고 있습니다.', 'SNS에서 알게 된 외국 지인이 선물을 보내준다며 제 주소로 택배를 보냈고, 실제로 받은 박스 안에 마약이 들어 있었다고 합니다. 저는 내용물을 모른 채 수령만 했는데, 경찰에서는 공범 혐의로 조사 중입니다.', null, null, null);

-- -----------------------------------------

select * from application_tag;
insert into application_tag (id, application_id, tag_id)
	values
		(1, 1, 3),
        (2, 2, 6),
        (3, 2, 44),
        (4, 3, 9),
        (5, 3, 29),
        (6, 3, 30),
        (7, 3, 31),
        (8, 3, 32),
        (9, 4, 10),
        (10, 4, 12),
        (11, 4, 13),
        (12, 4, 14),
        (13, 5, 13),
        (14, 5, 22),
        (15, 5, 23),
        (16, 5, 24);

-- -----------------------------------------

select * from appointment;
insert into appointment (id, application_id, client_id, lawyer_id, appointment_status, start_time, end_time, created_at)
	values
		(1, 1, 1, 5, 'ENDED', '2025-08-02 16:30:00', '2025-08-02 17:30:00', '2025-08-02 09:15:51'),
        (2, 2, 2, 1, 'CANCELLED', '2025-08-02 10:30:00', '2025-08-02 11:30:00', '2025-08-01 22:02:15'),
        (3, 2, 2, 4, 'IN_PROGRESS', '2025-08-07 14:00:00', '2025-08-07 15:00:00', '2025-08-05 16:57:13'),
        (4, 3, 3, 1, 'IN_PROGRESS', '2025-08-07 16:00:00', '2025-08-07 17:00:00', '2025-08-06 17:35:17'),
        (5, 3, 3, 2, 'CONFIRMED', '2025-08-10 15:30:00', '2025-08-10 14:30:00', '2025-08-05 10:17:18'),
        (6, 4, 4, 6, 'CONFIRMED', '2025-08-12 13:30:00', '2025-08-12 14:30:00', '2025-08-06 23:06:46'),
        (7, 5, 5, 4, 'PENDING', '2025-08-18 12:00:00', '2025-08-18 13:00:00', '2025-08-07 00:11:24');

-- -----------------------------------------

select * from unavailability_slot;
insert into unavailability_slot (id, lawyer_id, start_time, end_time)
values
	(1, 1, '2025-08-07 16:00:00', '2025-08-07 17:00:00'),
    (3, 2, '2025-08-10 15:30:00', '2025-08-10 14:30:00'),
    (4, 4, '2025-08-07 14:00:00', '2025-08-07 15:00:00'),
    (7, 6, '2025-08-12 13:30:00', '2025-08-12 14:30:00');
    
-- -----------------------------------------

select * from room;
insert into room (id, openvidu_custom_session_id, openvidu_session_id)
values
	(1, 'f81d4fae-7dec-11d0-a765-00a0c91e6bf6', 'f81d4fae-7dec-11d0-a765-00a0c91e6bf6'),
    (2, '3a7f8b9e-6c0d-4f5e-a1b2-3c4d5e6f7a8b', '3a7f8b9e-6c0d-4f5e-a1b2-3c4d5e6f7a8b');

-- -----------------------------------------

select * from participant;
insert into participant (id, room_id, client_id, lawyer_id)
values
	(1, 1, 2, null),
    (2, 1, null, 4),
    (3, 2, 3, null);

-- -----------------------------------------

select * from session;
insert into session (id, appointment_id, room_id, participant_count)
values
	(1, 3, 1, 2),
    (2, 4, 2, 1);

-- -----------------------------------------

select * from refresh_token;
insert into refresh_token (id, client_id, lawyer_id, admin_id, refresh_token, issued_at, revoked_at)
values
	(1, 1, null, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MzY1ODg3MDgxIiwiaWF0IjoxNzU0NTAyNjA1LCJleHAiOjE3NTUxMDc0MDV9.RfdSQueinN-GIPJABh8nLGByv0bHHEknc0odlssE0yY', '2025-08-07 02:55:00', '2025-08-14 02:55:00'),
    (2, 2, null, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MzgxNDc4MjI1IiwiaWF0IjoxNzU0NTAyNjA1LCJleHAiOjE3NTUxMDc0MDV9.8iAUldv7fOOajaS2His2N-OVxRtUmQkc1GE4i7gL8hE', '2025-08-07 02:55:00', '2025-08-14 02:55:00'),
    (3, 3, null, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MzYxNDY2MDk5IiwiaWF0IjoxNzU0NTAyNjA1LCJleHAiOjE3NTUxMDc0MDV9.n1A3XvSqFrMNRkXDMcugfMAoJC161Q8fOq6Lf0KXECU', '2025-08-07 02:55:00', '2025-08-14 02:55:00'),
    (4, 4, null, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0Mzg0MDkwODUxIiwiaWF0IjoxNzU0NTAyNjA1LCJleHAiOjE3NTUxMDc0MDV9.kBeWVArB3Omk8oKCxoYyxWni1VJYZT2CBThlfkjMjQQ', '2025-08-07 02:55:00', '2025-08-14 02:55:00'),
    (5, 5, null, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MzY1ODg3MDIxIiwiaWF0IjoxNzU0NTAyNjA1LCJleHAiOjE3NTUxMDc0MDV9.dorG7ZU8CHErD_hzx_3p8uNxTS_Ud-hVPxvKlc5McVg', '2025-08-07 02:55:00', '2025-08-14 02:55:00'),
    (6, 6, null, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MzY1ODg3OTY1IiwiaWF0IjoxNzU0NTAyNjA1LCJleHAiOjE3NTUxMDc0MDV9.2wXnonx3lIGp-3EiYnlSiUTB8CR2UXUBQ9q_RKWEM-M', '2025-08-07 02:55:00', '2025-08-14 02:55:00'),
    (7, 7, null, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MzY1ODg3MTUyIiwiaWF0IjoxNzU0NTAyNjA1LCJleHAiOjE3NTUxMDc0MDV9.DRG68hxOsu57eazvgjRwFhS_MtQ77NHa_csmcGJyaak', '2025-08-07 02:55:00', '2025-08-14 02:55:00'),
    (8, 8, null, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MzY1ODg3Nzg0IiwiaWF0IjoxNzU0NTAyNjA1LCJleHAiOjE3NTUxMDc0MDV9.Dgj4GxYBkjPZDpvWdflK8BqkwcJdWCQawMZUJYpnevs', '2025-08-07 02:55:00', '2025-08-14 02:55:00'),
    (9, 9, null, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MzY1ODg3MzY1IiwiaWF0IjoxNzU0NTAyNjA1LCJleHAiOjE3NTUxMDc0MDV9.Ogt2X5gutzQ7qXBL7ggjdKqKcYLCWX0g3qP8htGvlBI', '2025-08-07 02:55:00', '2025-08-14 02:55:00'),
    (10, 10, null, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MzY1ODg3ODQ1IiwiaWF0IjoxNzU0NTAyNjA1LCJleHAiOjE3NTUxMDc0MDV9.QWzkYSpXsb3VN3C7lq1SgQoDflbwvwjqfX1jajfqixc', '2025-08-07 02:55:00', '2025-08-14 02:55:00'),
	(11, null, 1, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzU0NTAzMTIzLCJleHAiOjE3NTUxMDc5MjN9.MDZ_yMAL9CjC88PqPTj-AKDptVxo06SedvaM1IId-HI', '2025-08-07 02:58:00', '2025-08-14 02:58:00'),
    (12, null, 2, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyIiwiaWF0IjoxNzU0NTAzMTI0LCJleHAiOjE3NTUxMDc5MjR9.V_uyJtkP_jUnGoHPqtxAfRBlnq9Tw6eMpOmrSXxJ0ng', '2025-08-07 02:58:00', '2025-08-14 02:58:00'),
    (13, null, 3, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIzIiwiaWF0IjoxNzU0NTAzMTI0LCJleHAiOjE3NTUxMDc5MjR9.yPMRhrt2r0hxL9rydvMeCMOItPX4inLqUIKVAjL3_Ag', '2025-08-07 02:58:00', '2025-08-14 02:58:00'),
    (14, null, 4, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0IiwiaWF0IjoxNzU0NTAzMTI0LCJleHAiOjE3NTUxMDc5MjR9.BPkGZ9AVwXOaG_mghPRhvlgN_xMER3oQLd-UeFDfn-Q', '2025-08-07 02:58:00', '2025-08-14 02:58:00'),
    (15, null, 5, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1IiwiaWF0IjoxNzU0NTAzMTI0LCJleHAiOjE3NTUxMDc5MjR9.pejgYS97YLDV6fWZV4kRIfqSHL8_Wi7l_4TrYfx_x8I', '2025-08-07 02:58:00', '2025-08-14 02:58:00'),
    (16, null, 6, null, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2IiwiaWF0IjoxNzU0NTAzMTI0LCJleHAiOjE3NTUxMDc5MjR9.PGm3OSyAqZCrAr35t2g39KgsRsbs7XqcfQ7_JSuMHK4', '2025-08-07 02:58:00', '2025-08-14 02:58:00'),
	(17, null, null, 1, 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJBRE1JTjphZG1pbkBhZG1pbi5jb20iLCJpYXQiOjE3NTQ1MDMyMzQsImV4cCI6MTc1NTEwODAzNH0.SpVrvXhI4PRyRddOP-IYRkYRi-9jUWD-pi6GxifdhVc', '2025-08-07 03:01:00', '2025-08-14 03:01:00');
