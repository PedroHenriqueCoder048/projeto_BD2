-- Demonstração: tabelas, INSERT, SELECT, erro e JOIN
CREATE TABLE aluno (id INT, nome CHAR(10));
CREATE TABLE nota (aluno_id INT, valor INT);
INSERT INTO aluno VALUES (1, 'ana');
INSERT INTO aluno VALUES (2, 'bia');
INSERT INTO nota VALUES (1, 9);
INSERT INTO nota VALUES (1, 7);
INSERT INTO nota VALUES (3, 5);
SELECT * FROM aluno;
SELECT * FROM aluno WHERE id = 2;
INSERT INTO aluno VALUES ('x', 1);
SELECT * FROM aluno JOIN nota ON aluno.id = nota.aluno_id;
