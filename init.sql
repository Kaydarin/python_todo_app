CREATE SCHEMA IF NOT EXISTS `python_todo`;

CREATE TABLE IF NOT EXISTS `python_todo`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `github_id` VARCHAR(128) NOT NULL,
  `github_username` VARCHAR(255) NOT NULL,
  `github_userurl` VARCHAR(255) NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NULL,
  `deleted_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `GITHUB_ID` USING BTREE (`github_id`));

CREATE TABLE IF NOT EXISTS `python_todo`.`tasks` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `title` VARCHAR(255) NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NULL,
  `deleted_at` DATETIME NULL,
  PRIMARY KEY (`id`));

CREATE TABLE IF NOT EXISTS `python_todo`.`todos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `task_id` INT NOT NULL,
  `title` VARCHAR(255) NULL,
  `is_done` TINYINT NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NULL,
  `deleted_at` DATETIME NULL,
  PRIMARY KEY (`id`));
