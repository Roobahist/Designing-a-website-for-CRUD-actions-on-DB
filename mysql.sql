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



INSERT INTO `role`(`role_id`, `role_name`) 
VALUES ('1','Manager'), ('2','staff'), ('3','role1'), ('4','role2');

INSERT INTO `department`(`department_id`, `department_name`, `number_of_employees`, `budget`, `manager_name`) 
VALUES ('1','qwe','15','3000','Mahsa'), ('2','asd','28','2500','Mojtaba'), ('3','hkj','9','680','Shahnaz'), ('4','slv','3','1750','sara');

INSERT INTO `employee`(`employee_id`, `ssn`, `name`, `age`, `gender`, `phone_number`, `address`, `income`, `role_id`, `department_id`) 
VALUES ('1', '159753', 'mahsa'   , '21', 'F', '0910939', 'karaj'   , '200000' , '1', '1' ), 
	   ('2', '236547', 'Mojtaba' , '21', 'M', '0918664', 'andishe' , '200000' , '1', '2' ),
	   ('3', '456321', 'Shahnaz' , '42', 'F', '0910939', 'tehran'  , '2362'   , '1', '3' ), 
	   ('4', '147896', 'sara'    , '26', 'F', '0918664', 'shiraz'  , '65846'  , '1', '4' ),
	   ('5', '159755', 'yasin'   , '21', 'M', '0918664', 'esfehan' , '135'    , '2', '2' ),
	   ('6', '132645', 'amir'    , '54', 'M', '0910939', 'karaj'   , '1002'   , '3', '3' ), 
	   ('7', '756982', 'bita'    , '53', 'F', '0918664', 'tehran'  , '1453'   , '4', '1' );

INSERT INTO `teacher` (`teacher_id`, `specialties`, `research_point`, `wage_per_hour`, `number_of_previous_students`) 
VALUES ('3', 'spec1', '100', '10000' , '88'), 
	   ('4', 'spec2', '218', '100000', '210'), 
	   ('7', 'spec2', '164', '50000' , '130');

INSERT INTO `course` (`course_id`, `course_name`, `course_desc`, `category`, `number_of_sessions`, `requirements`, `class_starting_time`, `class_finishing_time`, `exam_date`, `exam_starting_time`, `exam_finishing_time`, `department_id`, `teacher_id`, `starting_date`, `ending_date`) 
VALUES ('1', 'course_1', 'desc1', 'cat1', '40', '', '08:00:00.000000', '09:30:00.000000', '2021-01-06', '11:00:00.000000', '12:30:00.000000', '3', '3', '2021-01-03', '2021-01-04'),
       ('2', 'course_2', 'desc2', 'cat2', '87', '', '10:00:00.000000', '11:30:00.000000', '2021-03-07', '10:00:00.000000', '11:30:00.000000', '4', '4', '2021-01-12', '2021-03-05'),
	   ('3', 'course_3', 'desc3', 'cat1', '20', '', '12:00:00.000000', '13:30:00.000000', '2021-06-06', '08:00:00.000000', '09:30:00.000000', '4', '4', '2021-01-03', '2021-06-04'),
       ('4', 'course_4', 'desc4', 'cat3', '34', '', '08:00:00.000000', '09:30:00.000000', '2021-06-06', '08:00:00.000000', '09:30:00.000000', '1', '7', '2021-01-12', '2021-06-04');

INSERT INTO `course_class_days` (`course_id`, `holding_day`) 
VALUES ('1' , 'Sat'),
       ('1' , 'Mon'),
	   ('1' , 'Fri'),
	   ('2' , 'Sat'),
	   ('2' , 'Sun'),
	   ('3' , 'Mon'),
	   ('3' , 'Sun'),
	   ('3' , 'Wed'),
	   ('3' , 'Thu'),
	   ('4' , 'Mon');

INSERT INTO `employee_attends_course` (`participant_id`, `course_id`) 
VALUES ('2', '2'),('2', '3'),('4', '2');



