'''This file contains all the database logic to modify a character in the database, including
their characteristics, stats, abilities, and reputation.'''
import mysql.connector
class Sheet:
    """This class contains all the functions for adding, updating, and deleting 
    data from the database."""
    data = ""
    def connect(self, query, values, write, col):
        """This function connects to the mySQL database, executing queries and returning True
        if the queries went through, and False if they did not. It can read and write to the
        database, storing any data in a data tuple."""
        try:
            connection = mysql.connector.connect(host='localhost',
                                              database = 'characters',
                                              user = 'root',
                                              password = 'root')
            cursor = connection.cursor(buffered=True)
            if write:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
                if col:
                    self.data = cursor.fetchall()
                else:
                    self.data = cursor.fetchone()
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except mysql.connector.Error as error:
            print(f"Database error: {error}")
            cursor.close()
            connection.close()
            return False

    def register_char(self, args):
        """This function registers a new character into the database, taking in the inputs from
        the register character command. It puts those commands into the characteristics database,
        then inserts default values for the other databases."""
        mysql_insert_row_query = ("INSERT INTO characteristics (Name, Age, Species, Role, Gender, "+
        "Status, Starting_Weapon) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        mysql_insert_row_values = (str(args[0]), int(args[1]), str(args[2]), str(args[3]),
                                   str(args[4]), str(args[5]), str(args[6]))
        self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False)
        mysql_insert_row_query = ("INSERT INTO primary_stats (STR, DEX, PER, SRV, RES, END) " +
        "VALUES (DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT)")
        self.connect(mysql_insert_row_query, 0, True, False)
        mysql_insert_row_query = ("INSERT INTO secondary_stats (LVL, MAX_HP, HP, MAX_XP, XP, " +
        "RECOVERY, DAM, PRO, MOV, MAX_AMP, AMP, AMP_GAIN, INV, CRT) VALUES (DEFAULT, DEFAULT, " +
        "DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, " +
        "DEFAULT, DEFAULT, DEFAULT)")
        self.connect(mysql_insert_row_query, 0, True, False)
        self.calculate_stat(int(self.get_id(args[0])))
        mysql_insert_row_query = ("INSERT INTO ability_slots (slot_1, slot_2, slot_3) VALUES " +
        "(DEFAULT, DEFAULT, DEFAULT)")
        self.connect(mysql_insert_row_query, 0, True, False)
        mysql_insert_row_query = ("INSERT INTO reputation (government, resistance, fbl, " +
        "peace_corps) VALUES (DEFAULT, DEFAULT, DEFAULT, DEFAULT)")
        self.connect(mysql_insert_row_query, 0, True, False)

    def get_id(self, name):
        '''This function retrieves the ID of a character based on its name.'''
        print(name)
        mysql_insert_row_query = f"SELECT char_id FROM characteristics WHERE Name = '{name}'"
        self.connect(mysql_insert_row_query, 0, False, False)
        return self.clean_up(str(self.data)).replace(",", "")

    def calculate_stat(self, char_id):
        '''This function recalculates the secondary stats based on the primary stats.
        Then, it updates those stats in the database.'''
        mysql_insert_row_query = f"SELECT * FROM primary_stats WHERE char_id = {char_id}"
        self.connect(mysql_insert_row_query, 0, False, False)
        prim = self.data
        mysql_insert_row_query = f"SELECT * FROM secondary_stats WHERE char_id = {char_id}"
        self.connect(mysql_insert_row_query, 0, False, False)
        sec = self.data
        stats = self.calculations(prim, sec)
        mysql_insert_row_query = ("UPDATE secondary_stats SET MAX_HP = %s, MAX_XP = %s, " +
        "XP = %s, RECOVERY = %s, DAM = %s, PRO = %s, MOV = %s, MAX_AMP = %s, AMP = %s, " +
        "AMP_GAIN = %s, INV = %s, CRT = %s WHERE char_id = %s")
        mysql_insert_row_values = (stats[0], stats[1], stats[2], stats[3], stats[4], stats[5],
                                   stats[6],stats[7], stats[8], stats[9], stats[10], stats[11],
                                   char_id)
        self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False)

    def calculations(self, prim, sec):
        '''This function performs the necessary calculations of secondary stats,
        based on the primary stats.'''
        max_hp = 50 + (10 * int(prim[4])) + (5 * int(sec[0]))
        max_xp = (int(sec[0]) - 1) + 300
        xp = 0
        recovery = int(prim[3])
        dam = int(sec[0]) + int(prim[0])
        pro = int(prim[4])
        mov = int(prim[2]) - 2
        mov = max(mov, 1)
        max_amp = int(sec[0]) + (int(prim[5]) * 2)
        amp = max_amp
        amp_gain = int(prim[5]) - 5
        amp_gain = max(amp_gain, 1)
        inv = int(prim[3]) + 25
        crt = 10 + int(prim[2])
        return (max_hp, max_xp, xp, recovery, dam, pro, mov, max_amp, amp, amp_gain, inv, crt)

    def register_prim(self, args):
        '''This function registers the primary stats of characters by taking in each
        value, adding them to the database. It then calls the calculating stats function
        to recalculate secondary stats.'''
        mysql_insert_row_query = ("UPDATE primary_stats SET STR = %s, DEX = %s, PER = %s," +
                                  "SRV = %s, RES = %s, END = %s WHERE char_id = %s")
        mysql_insert_row_values = (str(args[0]), int(args[1]), str(args[2]), str(args[3]),
                                   str(args[4]), str(args[5]), str(args[6]))
        self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False)
        self.calculate_stat(str(args[6]))
    def level_up(self, stat, char_id):
        '''This function accurately levels up a character, increasing the level value, allowing
        the character to increment a primary stat by 1, including recalculating the secondary
        stats to account for that change.'''
        mysql_insert_row_query = "SELECT LVL FROM secondary_stats WHERE char_id = " + char_id
        self.connect(mysql_insert_row_query, 0, False, False)
        lvl = int(','.join([str(x) for x in self.data])) + 1
        mysql_insert_row_query = "UPDATE secondary_stats SET LVL = %s WHERE char_id = " + char_id
        mysql_insert_row_values = (lvl,)
        self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False)
        mysql_insert_row_query = ("SELECT " + stat.upper() + " " +
        "FROM primary_stats WHERE char_id = " + char_id)
        if self.connect(mysql_insert_row_query, 0, False, False) is False:
            return False
        print(self.data)
        self.data = int(','.join([str(x) for x in self.data])) + 1
        mysql_insert_row_query = ("UPDATE primary_stats SET " + stat.upper() + " = %s " +
        "WHERE char_id = " + char_id)
        mysql_insert_row_values = (self.data,)
        self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False)
        self.calculate_stat(char_id)
        return True

    def edit_char(self, column, char_id, value):
        '''This function enables the user to edit character properties, given
        the column, value, and the ID of the character.'''
        mysql_insert_row_query = ("UPDATE characteristics SET " + column + " " +
        "= %s WHERE char_id = " + char_id)
        mysql_insert_row_values = (value,)
        if self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False) is False:
            return False
        return True

    def edit_prim(self, column, char_id, value):
        '''This function enables the user to edit primary stats of a character, given
        the stat, value, and the ID of the character. It also calls the function to 
        recalculate secondary stats.'''
        mysql_insert_row_query = ("UPDATE primary_stats SET " + column + " = %s" +
        " WHERE char_id = " + char_id)
        mysql_insert_row_values = (value,)
        if self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False) is False:
            return False
        self.calculate_stat(char_id)
        return True

    def find_rep(self, col, row, char_id):
        '''This function finds the reputation data of a character given its ID,
        and passes a function to update the reputation of the character in the 
        database.'''
        group = ""
        tup = ()
        tup2 = ()
        if int(col) == 0:
            group = "GOVERNMENT:"
            mysql_insert_row_query = "SELECT government FROM rep_names "
            self.connect(mysql_insert_row_query, 0, False, True)
            tup = self.data
            mysql_insert_row_query = "SELECT government FROM rep_desc "
            self.connect(mysql_insert_row_query, 0, False, True)
            tup2 = self.data
        elif int(col) == 1:
            group = "THORNLING RESISTANCE:"
            mysql_insert_row_query = "SELECT resistance FROM rep_names "
            self.connect(mysql_insert_row_query, 0, False, True)
            tup = self.data
            mysql_insert_row_query = "SELECT resistance FROM rep_desc "
            self.connect(mysql_insert_row_query, 0, False, True)
            tup2 = self.data
        elif int(col) == 2:
            group = "FREE BLACKTHORN LEAGUE:"
            mysql_insert_row_query = "SELECT fbl FROM rep_names "
            self.connect(mysql_insert_row_query, 0, False, True)
            tup = self.data
            mysql_insert_row_query = "SELECT fbl FROM rep_desc "
            self.connect(mysql_insert_row_query, 0, False, True)
            tup2 = self.data
        else:
            group = "PEACE CORPS:"
            mysql_insert_row_query = "SELECT 'peace_corps' FROM rep_names "
            self.connect(mysql_insert_row_query, 0, False, True)
            tup = self.data
            mysql_insert_row_query = "SELECT 'peace_corps' FROM rep_desc "
            self.connect(mysql_insert_row_query, 0, False, True)
            tup2 = self.data
        self.update_rep(char_id, col, self.clean_up(str(tup[int(row)]).replace
                                                  ("'", "").replace(",", "")))
        return (group + self.clean_up(str(tup[int(row)]).replace("'", "").replace(",", ""))
                + " - " + self.clean_up(str(tup2[int(row)]).replace("'", "").replace(",", "")))

    def update_rep(self, char_id, col, values):
        '''This function updates the reputation of a given character given its ID,
        the group column, and the value you wish to change it to.'''
        mysql_insert_row_query = ("SELECT char_id FROM reputation WHERE char_id = " +
        + char_id + " LIMIT 1")
        self.connect(mysql_insert_row_query, 0, False, False)
        if self.data is None:
            mysql_insert_row_query = ("INSERT INTO reputation (government, resistance, " +
            "fbl, peace_corps, char_id) VALUES (%s, %s, %s, %s, %s)")
            if int(col) == 0:
                mysql_insert_row_values = (values, None, None, None, char_id)
            elif int(col) == 1:
                mysql_insert_row_values = (None, values, None, None, char_id)
            elif int(col) == 2:
                mysql_insert_row_values = (None, None, values, None, char_id)
            else:
                mysql_insert_row_values = (None, None, None, values, char_id)
            self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False)

        else:
            if int(col) == 0:
                mysql_insert_row_query = ("UPDATE reputation SET government = %s " +
                "WHERE char_id = " + char_id)
            elif int(col) == 1:
                mysql_insert_row_query = ("UPDATE reputation SET resistance = %s " +
                "WHERE char_id = " + char_id)
            elif int(col) == 2:
                mysql_insert_row_query = "UPDATE reputation SET fbl = %s WHERE char_id = " + char_id
            else:
                mysql_insert_row_query = ("UPDATE reputation SET peace_corps = %s " +
                "WHERE char_id = " + char_id)
            mysql_insert_row_values = (values,)
            self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False)

    def clean_up(self, string):
        '''This function cleans up strings returned from the database, by removing outermost
        parentheses.'''
        n = len(string)
        cnt = 0
        while (cnt < n and string[cnt] == '(' and string[n - cnt - 1] == ')'):
            cnt += 1
        cnt_min_par = 0
        cnt_unbal = 0
        for i in range(cnt, n - cnt):
            if string[i] == '(':
                cnt_unbal += 1
            elif string[i] == ')':
                cnt_unbal -= 1
            cnt_min_par = min(cnt_min_par, cnt_unbal)
        cnt += cnt_min_par
        return string[cnt: n-cnt]

    def calculate_slots(self, char_id):
        '''This function calculates the amount of slots available for the character
        using the character's LEVEL.'''
        mysql_insert_row_query = "SELECT LVL FROM secondary_stats WHERE char_id = " + char_id
        self.connect(mysql_insert_row_query, 0, False, False)
        val = int(self.data[0])
        if val < 10:
            return 1
        if 10 < val < 20:
            return 2
        return 3

    def update_abilities(self, char_id, slots, values):
        '''This function inserts inputted abilities into the ability database for each character
        given the amount of the slots available and the ability inputted.'''
        mysql_insert_row_query = ("SELECT char_id FROM ability_slots WHERE " +
        "char_id = " + char_id + " LIMIT 1")
        self.connect(mysql_insert_row_query, 0, False, False)
        if self.data is None:
            mysql_insert_row_query = ("INSERT INTO ability_slots (slot_1, slot_2, slot_3, " +
            "char_id) VALUES (%s, %s, %s, %s)")
            if slots == 1:
                mysql_insert_row_values = (values, None, None, char_id)
            elif slots == 2:
                mysql_insert_row_values = (None, values, None, char_id)
            else:
                mysql_insert_row_values = (None, None, values, char_id)
            self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False)
        else:
            mysql_insert_row_query = ("UPDATE ability_slots SET slot_" + str(slots)
                                      + " = %s WHERE char_id = " + char_id)
            mysql_insert_row_values = (values,)
            self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False)


    def delete_sheet(self, char_id):
        '''This function deletes a sheet from the database, by deleting every table that has
        the character's character id.'''
        mysql_insert_row_query = "DELETE FROM characteristics WHERE char_id = " + char_id
        self.connect(mysql_insert_row_query, 0, False, True)
        mysql_insert_row_query = "DELETE FROM primary_stats WHERE char_id = " + char_id
        self.connect(mysql_insert_row_query, 0, False, True)
        mysql_insert_row_query = "DELETE FROM secondary_stats WHERE char_id = " + char_id
        self.connect(mysql_insert_row_query, 0, False, True)
        mysql_insert_row_query = "DELETE FROM ability_slots WHERE char_id = " + char_id
        self.connect(mysql_insert_row_query, 0, False, True)
        mysql_insert_row_query = "DELETE FROM reputation WHERE char_id = " + char_id
        self.connect(mysql_insert_row_query, 0, False, True)
    def verify_id(self, char_id):
        '''This function searchs for if a given character exists in the database, and returns
        false if the id doesn't exist.'''
        mysql_insert_row_query = ("SELECT * FROM characteristics WHERE EXISTS (SELECT * " +
                                  "FROM characteristics WHERE char_id = " + char_id)
        self.connect(mysql_insert_row_query, 0, False, False)
        if self.data is None:
            return False
        return True
