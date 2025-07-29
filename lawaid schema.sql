drop database if exists lawaid;

create database lawaid;
use lawaid;

create table client (
	id int unsigned auto_increment primary key,
    name varchar(20) not null,
    email varchar(30) unique not null,
    oauth_provider varchar(20) not null,
    oauth_identifier varchar(30) not null
);

create table lawyer (
	id int unsigned auto_increment primary key,
	login_email varchar(100) unique not null,
    login_password_hash varchar(100) not null, -- 비밀번호가 30byte 제한이라면, 단방향 암호화하고 Base64로 저장했을때 100byte를 절대 넘지 않을 것
    photo text,
    name varchar(30) not null,
    introduction text,
    exam varchar(50),
    registration_number varchar(50) not null,
    certification_status enum('PENDING', 'APPROVED', 'REJECTED') not null default 'PENDING',
    consultation_count int unsigned not null default 0
);

create table unavalability_slot (
	id int unsigned auto_increment primary key,
    lawyer_id int unsigned not null,
    start_time datetime not null,
    end_time datetime not null,
    
    constraint fk_unavalability_slot_lawyer_id
		foreign key (lawyer_id) references lawyer(id)
        on delete cascade
        on update cascade
);

create table refresh_token (
	id int unsigned auto_increment primary key,
    client_id int unsigned,
    lawyer_id int unsigned,
    refresh_token text not null,
    issued_at datetime not null,
    revoked_at datetime,
    
    constraint fk_refresh_token_client_id
		foreign key (client_id) references client(id)
        on delete cascade
        on update cascade,
	
    constraint fk_refresh_token_lawyer_id
		foreign key (lawyer_id) references lawyer(id)
        on delete cascade
        on update cascade
);

create table application (
	id int unsigned auto_increment primary key,
    client_id int unsigned not null,
    title text not null,
    summary text not null,
    content text not null,
    outcome text,
    disadvantage text,
    recommended_questions json,
    is_completed boolean not null default false,
    created_at datetime not null default current_timestamp,
    
    constraint fk_application_client_id
		foreign key (client_id) references client(id)
        on delete cascade
        on update cascade
);

create table tag (
	id int unsigned auto_increment primary key,
    name varchar(50) unique not null
);

create table lawyer_tag (
	id int unsigned auto_increment primary key,
    lawyer_id int unsigned not null,
    tag_id int unsigned not null,
    
    constraint fk_lawyer_tag_lawyer_id
		foreign key (lawyer_id) references lawyer(id)
        on delete cascade
        on update cascade,
        
	constraint fk_lawyer_tag_tag_id
		foreign key (tag_id) references tag(id)
        on delete cascade
        on update cascade
);

create table application_tag (
	id int unsigned auto_increment primary key,
    application_id int unsigned not null,
    tag_id int unsigned not null,
    
    constraint fk_application_tag_application_id
		foreign key (application_id) references application(id)
        on delete cascade
        on update cascade,
	
    constraint fk_application_tag_tag_id
		foreign key (tag_id) references tag(id)
        on delete cascade
        on update cascade
);

create table appointment (
	id int unsigned auto_increment primary key,
    client_id int unsigned not null,
    lawyer_id int unsigned not null,
    application_id int unsigned not null,
    appointment_status enum('PENDING', 'CONFIRMED', 'REJECTED', 'IN_PROGRESS', 'CANCELED', 'ENDED') not null default 'PENDING',
    start_time datetime not null,
    end_time datetime not null,
    created_at datetime not null default current_timestamp,
    
    constraint fk_appointment_client_id
		foreign key (client_id) references client(id)
        on delete cascade
        on update cascade,
        
	constraint fk_appointment_lawyer_id
		foreign key (lawyer_id) references lawyer(id)
        on delete cascade
        on update cascade,
        
	constraint fk_appointment_application_id
		foreign key (application_id) references application(id)
        on delete cascade
        on update cascade
);

create table room (
	id int unsigned auto_increment primary key,
    openvidu_session_id varchar(100) not null, -- 아니 뭐.. 오픈비두 세션 아이디가 100byte를 넘진 않겟져?
    openvidu_custom_session_id varchar(100) not null
);

create table session (
	id int unsigned auto_increment primary key,
    appointment_id int unsigned not null,
    room_id int unsigned not null,
    participants_count tinyint unsigned not null default 0,
    
    constraint fk_session_appointment_id
		foreign key (appointment_id) references appointment(id)
        on delete cascade
        on update cascade,
        
	constraint fk_session_room_id
		foreign key (room_id) references room(id)
        on delete cascade
        on update cascade
);

create table participant (
	id int unsigned auto_increment primary key,
    room_id int unsigned not null,
    client_id int unsigned not null,
    lawyer_id int unsigned not null,
    
	constraint fk_participant_room_id
		foreign key (room_id) references room(id)
		on delete cascade
		on update cascade,
        
	constraint fk_participant_client_id
		foreign key (client_id) references client(id)
		on delete cascade
		on update cascade,
        
	constraint fk_participant_lawyer_id
		foreign key (lawyer_id) references lawyer(id)
		on delete cascade
		on update cascade
)