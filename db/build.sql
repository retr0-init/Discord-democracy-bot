CREATE TABLE IF NOT EXISTS USER (
	user_id INT PRIMARY KEY,
	user_join_date DATETIME,
	user_roles INTEGER[], -- list of discord.Role, get from member.roles
	punishments INTEGER[], -- UUID TYPE?
	cases INTEGER[] -- UUID TYPE
);

CREATE TABLE IF NOT EXISTS VOTE (
	vote_id INT PRIMARY KEY, -- UUID TYPE?
	vote_created DATETIME,
	vote_expiry DATETIME,
	finished BOOLEAN, -- Whether this vote has been ended
	vote_type INT, -- Enum of the vote type
	voter_limited BOOLEAN, -- Whether this vote is limited to specific members only
	voters INTEGER[] -- This should be NULL if voter_limited is FALSE
);

CREATE TABLE IF NOT EXISTS CASES (
	case_id INT PRIMARY KEY, -- UUID TYPE?
	case_created DATETIME,
	appleallees INTEGER[], -- This should link to the USER's user_id
	appeallors INTEGER[], -- This should link to the USER's user_id
	case_step INT, -- Enum of the case step
	votes INT[], -- This should link to the VOTE's vote_id
);

CREATE TABLE IF NOT EXISTS PUNISHMENT (
	punishment_id INT PRIMARY KEY, -- UUID TYPE?
	punishment_created DATETIME,
	-- The expiry time of the punishment. What if it is the one-time type?
	-- Could be NULL if the punishment_type is some specific ones.
	punishment_expiry DATETIME,
	punishment_type INT, -- Enum of the punishment type
	completed BOOLEAN, -- Whether this punishment is finished
	issued_authority INT,
	issued_by INT[]
);
