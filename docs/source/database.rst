========
Database
========


.. toctree::

.. _database:

********************
Database Information
********************

Creation
========

.. code-block:: sql

    CREATE TABLE users (
            `id` INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
            `tid` BIGINT UNIQUE NOT NULL,
            `username` VARCHAR(255),
            `name` VARCHAR(255),
            `balance` MEDIUMINT NOT NULL DEFAULT 0,
            `permission` BOOLEAN NOT NULL DEFAULT false,
            `tscreated` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            `tsaccessed` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    CREATE TABLE transactions (
            `id` INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
            `fromuser` INT NOT NULL,
            `touser` INT NOT NULL,
            `amount` MEDIUMINT NOT NULL,
            `reason` VARCHAR(255),
            `transtime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (touser) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (fromuser) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE collectives (
            `id` INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
            `active` BOOLEAN NOT NULL,
            `amount` MEDIUMINT NOT NULL,
            `externs` SMALLINT,
            `descr` VARCHAR(255),
            `flag` BOOLEAN NOT NULL,
            `users_id` INT NOT NULL,
            FOREIGN KEY (users_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE collectives_users (
            `id` INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
            `collectives_id` INT NOT NULL,
            `users_id` INT NOT NULL,
            `vote` ENUM('-', '.', '+') NOT NULL,
            FOREIGN KEY (collectives_id) REFERENCES collectives(id) ON DELETE CASCADE,
            FOREIGN KEY (users_id) REFERENCES users(id) ON DELETE CASCADE
    );


Description
===========


Table users
^^^^^^^^^^^

+------------+--------------+------+-----+-------------------+-----------------------------+
| Field      | Type         | Null | Key | Default           | Extra                       |
+============+==============+======+=====+===================+=============================+
| id         | int(11)      | NO   | PRI | NULL              | auto_increment              |
+------------+--------------+------+-----+-------------------+-----------------------------+
| tid        | bigint(20)   | NO   | UNI | NULL              |                             |
+------------+--------------+------+-----+-------------------+-----------------------------+
| username   | varchar(255) | YES  |     | NULL              |                             |
+------------+--------------+------+-----+-------------------+-----------------------------+
| name       | varchar(255) | YES  |     | NULL              |                             |
+------------+--------------+------+-----+-------------------+-----------------------------+
| balance    | mediumint(9) | NO   |     | 0                 |                             |
+------------+--------------+------+-----+-------------------+-----------------------------+
| permission | tinyint(1)   | NO   |     | 0                 |                             |
+------------+--------------+------+-----+-------------------+-----------------------------+
| tscreated  | timestamp    | NO   |     | CURRENT_TIMESTAMP |                             |
+------------+--------------+------+-----+-------------------+-----------------------------+
| tsaccessed | timestamp    | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
+------------+--------------+------+-----+-------------------+-----------------------------+

The `tid` value is the Telegram user ID.

The `username` is the Telegram username (starting with `@`)
if this was set. Otherwise, `username` equals to `name`.
The `name` is the Telegram name consisting of the first and
last name (as far as this was set). You can be sure that
`username` and `name` will always be strings.

The `balance` is measured in Cent.

The `permission` flag should always be `FALSE` (or zero).
Any user who is whitelisted will get the positive flag.
This means that the user is permitted to vote on payment operations.

Table transactions
^^^^^^^^^^^^^^^^^^

+-----------+--------------+------+-----+-------------------+----------------+
| Field     | Type         | Null | Key | Default           | Extra          |
+===========+==============+======+=====+===================+================+
| id        | int(11)      | NO   | PRI | NULL              | auto_increment |
+-----------+--------------+------+-----+-------------------+----------------+
| fromuser  | int(11)      | NO   | MUL | NULL              |                |
+-----------+--------------+------+-----+-------------------+----------------+
| touser    | int(11)      | NO   | MUL | NULL              |                |
+-----------+--------------+------+-----+-------------------+----------------+
| amount    | mediumint(9) | NO   |     | NULL              |                |
+-----------+--------------+------+-----+-------------------+----------------+
| reason    | varchar(255) | YES  |     | NULL              |                |
+-----------+--------------+------+-----+-------------------+----------------+
| transtime | timestamp    | NO   |     | CURRENT_TIMESTAMP |                |
+-----------+--------------+------+-----+-------------------+----------------+

The `amount` is measured in Cent.

Table collectives
^^^^^^^^^^^^^^^^^

+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+==========+==============+======+=====+=========+================+
| id       | int(11)      | NO   | PRI | NULL    | auto_increment |
+----------+--------------+------+-----+---------+----------------+
| active   | tinyint(1)   | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
| amount   | mediumint(9) | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
| externs  | smallint(6)  | YES  |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
| descr    | varchar(255) | YES  |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
| flag     | tinyint(1)   | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
| users_id | int(11)      | NO   | MUL | NULL    |                |
+----------+--------------+------+-----+---------+----------------+

After committing the transaction(s) successfully,
the `active` flag should be set to `FALSE` (previously `TRUE`).

The `amount` is considered to be in Cent.

The counter `externs` must be positive. It is ignored if it's no communism.

The `flag` should be a boolean value. If it's `FALSE`,
then the collective operation is a payment.
Otherwise it is a communism.
The `externs` will be ignored on payments.

The `users_id` field was named `creator` earlier.
It refers to the user who created the collective operation.

Table collectives_users
^^^^^^^^^^^^^^^^^^^^^^^

+----------------+-------------------+------+-----+---------+----------------+
| Field          | Type              | Null | Key | Default | Extra          |
+================+===================+======+=====+=========+================+
| id             | int(11)           | NO   | PRI | NULL    | auto_increment |
+----------------+-------------------+------+-----+---------+----------------+
| collectives_id | int(11)           | NO   | MUL | NULL    |                |
+----------------+-------------------+------+-----+---------+----------------+
| users_id       | int(11)           | NO   | MUL | NULL    |                |
+----------------+-------------------+------+-----+---------+----------------+
| vote           | enum('-','.','+') | NO   |     | NULL    |                |
+----------------+-------------------+------+-----+---------+----------------+

This table maps collectives and users together.

The `vote` has the following meaning:

- `.` means ignoring the entry as the collective is a payment
- `-` means a disapproving vote by the specified user
- `+` means an approving vote by the specified user