-- Synthetic demonstration records only. Never use these as production data.
INSERT INTO role (role_id, role_name) VALUES
  (1, 'Manager'), (2, 'Staff'), (3, 'Trainer'), (4, 'Assistant');

INSERT INTO department (department_id, department_name, number_of_employees, budget, manager_name) VALUES
  (1, 'Engineering', 3, 3000, 'Example Manager A'),
  (2, 'Operations', 2, 2500, 'Example Manager B'),
  (3, 'Training', 2, 1500, 'Example Manager C'),
  (4, 'Research', 0, 1750, 'Example Manager D');

-- The original dataset omitted the mandatory employee.since column.
INSERT INTO employee (
  employee_id, ssn, name, age, gender, phone_number, address, income,
  role_id, department_id, since
) VALUES
  (1, 900001, 'Example Employee 1', 30, 'F', 100001, 'Example Address 1', 50000, 1, 1, '2021-01-01'),
  (2, 900002, 'Example Employee 2', 28, 'M', 100002, 'Example Address 2', 49000, 1, 2, '2021-01-01'),
  (3, 900003, 'Example Employee 3', 39, 'F', 100003, 'Example Address 3', 55000, 3, 3, '2021-01-01'),
  (4, 900004, 'Example Employee 4', 34, 'M', 100004, 'Example Address 4', 55000, 3, 3, '2021-01-01'),
  (5, 900005, 'Example Employee 5', 25, 'M', 100005, 'Example Address 5', 41000, 2, 2, '2021-01-01'),
  (6, 900006, 'Example Employee 6', 29, 'M', 100006, 'Example Address 6', 43000, 2, 1, '2021-01-01'),
  (7, 900007, 'Example Employee 7', 35, 'F', 100007, 'Example Address 7', 54000, 3, 1, '2021-01-01');

INSERT INTO skill (skill_id, skill_name, skill_desc) VALUES
  (1, 'SQL', 'Working with relational databases'),
  (2, 'Python', 'Python programming'),
  (3, 'Communication', 'Professional communication');

INSERT INTO teacher (teacher_id, specialties, research_point, wage_per_hour, number_of_previous_students) VALUES
  (3, 'Database design', 100, 100, 88),
  (4, 'Programming', 218, 100, 210),
  (7, 'Team skills', 164, 50, 130);

INSERT INTO course (
  course_id, course_name, course_desc, category, number_of_sessions, requirements,
  starting_date, ending_date, class_starting_time, class_finishing_time,
  exam_date, exam_starting_time, exam_finishing_time, department_id, teacher_id
) VALUES
  (1, 'Databases', 'Introductory SQL', 'Technical', 12, '', '2021-01-03', '2021-02-04', '08:00:00', '09:30:00', '2021-02-06', '11:00:00', '12:30:00', 3, 3),
  (2, 'Programming', 'Python basics', 'Technical', 10, '', '2021-01-12', '2021-03-05', '10:00:00', '11:30:00', '2021-03-07', '10:00:00', '11:30:00', 3, 4),
  (3, 'Communication', 'Team collaboration', 'Professional', 8, '', '2021-01-03', '2021-06-04', '12:00:00', '13:30:00', '2021-06-06', '08:00:00', '09:30:00', 3, 7);

INSERT INTO course_class_days (course_id, holding_day) VALUES
  (1, 'Mon'), (1, 'Fri'), (2, 'Tue'), (2, 'Thu'), (3, 'Wed');

INSERT INTO course_gives_skill (course_id, skill_id) VALUES
  (1, 1), (2, 2), (3, 3);

INSERT INTO employee_has_skill (employee_id, skill_id) VALUES
  (3, 1), (4, 2), (7, 3);

INSERT INTO employee_attends_course (participant_id, course_id) VALUES
  (2, 1), (2, 2), (5, 3);

INSERT INTO employee_takes_exam (participant_id, course_id, attempt_number, score, pass_or_fail) VALUES
  (2, 1, 1, 92, 'pass');
