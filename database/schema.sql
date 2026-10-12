create table department
(
	department_id int not null,
	department_name char(60) not null,
	number_of_employees int not null,
	budget real not null,
	manager_name char(60),
	manages_since date,
	primary key (department_id)
);

create table role
(	
	role_id int not null,
	role_name char(50) not null,
	role_desc longtext,
	primary key (role_id)
);

create table employee
(
	employee_id int not null,
	ssn int not null,
	name char(20) not null,
	age int,
	gender char(1) not null,
	phone_number int not null,
	address longtext not null,
	income real not null,
	role_id int not null,
	department_id int not null,
	since date not null,
	until date,
	unique (ssn),
	primary key (employee_id),
	foreign key (department_id) references department(department_id) on update cascade,
	foreign key (role_id) references role(role_id) on update cascade
);


create table skill
(	
	skill_id int not null,
	skill_name char(50) not null,
	skill_desc longtext,
	primary key (skill_id)
);


create table teacher
(
	teacher_id int not null,
	specialties longtext,
	research_point int,
	wage_per_hour int,
	number_of_previous_students int,
	foreign key (teacher_id) references employee(employee_id) on update cascade,
	primary key (teacher_id)
);


create table course
(
	course_id int not null,
	course_name char(30) not null,
	course_desc longtext,
	category char(40),
	number_of_sessions int,
	requirements longtext,
	starting_date date not null,
	ending_date date,
	class_starting_time time(6) not null,
	class_finishing_time time(6) not null,
	exam_date date not null,
	exam_starting_time time(6) not null,
	exam_finishing_time time(6) not null,
	department_id int not null,
	teacher_id int not null,
	primary key (course_id),
	foreign key (department_id) references department(department_id) on update cascade,
	foreign key (teacher_id) references teacher(teacher_id) on update cascade
);

create table course_class_days
(
	course_id int not null,
	holding_day char(3) not null,
	primary key (course_id,holding_day),
	foreign key (course_id) references course(course_id) on update cascade
);

create table course_gives_skill
(
	course_id int not null,
	skill_id int not null,
	foreign key (course_id) references course(course_id) on update cascade,
	foreign key (skill_id) references skill(skill_id) on update cascade,
	primary key (course_id,skill_id)
);

create table employee_has_skill
(
	employee_id int,
	skill_id int,
	foreign key (employee_id) references employee(employee_id) on update cascade,
	foreign key (skill_id) references skill(skill_id) on update cascade,
	primary key (employee_id,skill_id)
);


create table employee_attends_course
(
	participant_id int not null,
	course_id int not null,
	foreign key (participant_id) references employee(employee_id) on update cascade,
	foreign key (course_id) references course(course_id) on update cascade,
	primary key (participant_id,course_id)
);

create table employee_takes_exam
(
	participant_id int not null,
	course_id int not null,
	attempt_number int not null,
	score int not null,
	pass_or_fail char(4) not null,
	foreign key (participant_id,course_id) references employee_attends_course(participant_id,course_id) on update cascade,
	primary key (participant_id,course_id,attempt_number)
);
