INSERT INTO users(email, password, forename, surname, jmbg) values ("admin@admin.com", "123", "admin", "admin", "1111111111111");
INSERT into roles(name) values ("admin");
INSERT INTO roles(name) values ("electionOffical");
INSERT INTO userrole(userId, roleId) values (1, 1);