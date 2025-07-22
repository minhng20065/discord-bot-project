'''This file contains all the functions to retrieve and calculate from items in the database.'''
from sheet import Sheet
class Select:
    """This class contains all the functions for reading
    data from the database."""
    sheet = Sheet()
    def calculate_abilities(self, char_id):
        '''This function collects all the valid abilities given to the character,
        calculated by the characters' primary stats.'''
        abilities = ""
        temp = 0
        self.select_primary(char_id)
        tup = self.sheet.data
        val = ""
        desc = ""
        for x in range(len(tup)-1):
            mysql_insert_row_query = " "
            if x == 0:
                mysql_insert_row_query = "SELECT STR FROM abilities "
                mysql_insert_row_query2 = "SELECT STR FROM ability_desc "
            elif x == 1:
                mysql_insert_row_query = "SELECT DEX FROM abilities "
                mysql_insert_row_query2 = "SELECT DEX FROM ability_desc "
            elif x == 2:
                mysql_insert_row_query = "SELECT PER FROM abilities "
                mysql_insert_row_query2 = "SELECT PER FROM ability_desc "
            elif x == 3:
                mysql_insert_row_query = "SELECT SRV FROM abilities "
                mysql_insert_row_query2 = "SELECT SRV FROM ability_desc "
            elif x == 4:
                mysql_insert_row_query = "SELECT RES FROM abilities "
                mysql_insert_row_query2 = "SELECT SRV FROM ability_desc "
            else:
                mysql_insert_row_query = "SELECT END FROM abilities "
                mysql_insert_row_query2 = "SELECT END FROM ability_desc "
            self.sheet.connect(mysql_insert_row_query, 0, False, True)
            val = self.sheet.data
            self.sheet.connect(mysql_insert_row_query2, 0, False, True)
            desc = self.sheet.data
            print(val)
            temp = int(tup[x])
            if temp % 2 == 0:
                temp = temp - 1
            print(temp)
            for y in range(5, temp, 2):
                abilities = (abilities + self.sheet.clean_up(str(val[((y-3)//2) - 1]).
                                                      replace("'", "").replace(",", "")) +
                                                      " - " + self.sheet.clean_up(str(desc
                                                    [((y-3)//2) - 1]).replace("'", "").
                                                    replace(",", "") + " - " + str(y) + " AMP\n"))
        return abilities

    def select_char(self, char_id):
        '''This function selects all the characteristic data for a character given its
        character id.'''
        mysql_insert_row_query = "SELECT * FROM characteristics WHERE char_id = " + char_id
        self.sheet.connect(mysql_insert_row_query, 0, False, False)

    def select_primary(self, char_id):
        '''This function selects all the primary stats for a character given its 
        character id.'''
        mysql_insert_row_query = "SELECT * FROM primary_stats WHERE char_id = " + char_id
        self.sheet.connect(mysql_insert_row_query, 0, False, False)

    def select_secondary(self, char_id):
        '''This function selects all the secondary stats for a character given its 
        character id.'''
        mysql_insert_row_query = "SELECT * FROM secondary_stats WHERE char_id = " + char_id
        self.sheet.connect(mysql_insert_row_query, 0, False, False)

    def select_ability(self, char_id, slot):
        '''This function selects all the ability slots for a character given its 
        character id.'''
        mysql_insert_row_query = ("SELECT slot_" + str(slot) + " FROM " +
        "ability_slots WHERE char_id = " + char_id)
        self.sheet.connect(mysql_insert_row_query, 0, False, False)

    def select_rep(self, char_id):
        '''This function selects all the reputation slots for a character given its 
        character id.'''
        mysql_insert_row_query = "SELECT * FROM reputation WHERE char_id = " + char_id
        self.sheet.connect(mysql_insert_row_query, 0, False, False)

    def print_char(self, char_id):
        '''This function prints the characteristic data by retrieving
        it from the database and returning a string representation of the
        data.'''
        self.select_char(char_id)
        tup = self.sheet.data
        return ("Name: " + str(tup[0]) + "\nAge: " + str(tup[1]) + "\nSpecies: " +
                str(tup[2]) + "\nRole: " + str(tup[3]) + "\nGender: " + str(tup[4])
                  + "\nStatus: " + str(tup[5]) + "\nStarting Weapon: " + str(tup[6]))

    def print_prim(self, char_id):
        '''This function prints the primary data by retrieving
        it from the database and returning a string representation of the
        data.'''
        self.select_primary(char_id)
        tup = self.sheet.data
        return ("STR: " + str(tup[0]) + "\nDEX: " + str(tup[1]) + "\nPER: " + str(tup[2]) +
                "\nSRV: " + str(tup[3]) + "\nRES: " + str(tup[4]) + "\nEND: " + str(tup[5]))

    def print_sec(self, char_id):
        '''This function prints the secondary data by retrieving
        it from the database and returning a string representation of the
        data.'''
        self.select_secondary(char_id)
        tup = self.sheet.data
        return ("LVL: " + str(tup[0]) + "\nHP: " + str(tup[2]) + "/" + str(tup[1]) + "\nXP: "
                + str(tup[4]) + "/" + str(tup[3]) + "\nHP RECOVERY: " + str(tup[5]) + "\nDAM: "
                + str(tup[6]) + "\nPRO: " + str(tup[7]) + "\nMOV: " + str(tup[8]) + "\nAMP: " +
                str(tup[10]) + "/" + str(tup[9]) + "\nAMP GAIN: " + str(tup[11]) + "\nINV: " +
                str(tup[12]) + "\nCRT: " + str(tup[13]) + "%")

    def print_ability(self, char_id):
        '''This function prints the ability data by retrieving
        it from the database and returning a string representation of the
        data.'''
        ability = ""
        tup = ()
        for x in range(1, 4):
            self.select_ability(char_id, x)
            tup = tup + self.sheet.data
        for i in tup:
            if i is not None:
                ability = ability + str(i)
        return ability

    def print_rep(self, char_id):
        '''This function prints the reputation data by retrieving
        it from the database and returning a string representation of the
        data.'''
        rep = ""
        self.select_rep(char_id)
        tup = self.sheet.data
        for i in range(0, 4):
            if i == 0:
                rep = rep + "Government: "
                if tup[i] is not None:
                    rep = rep + str(tup[i]) + "\n"
                else:
                    rep = rep + "\n"
                return rep
            if i == 1:
                rep = rep + "Resistance: "
                if tup[i] is not None:
                    rep = rep + str(tup[i]) + "\n"
                else:
                    rep = rep + "\n"
                return rep
            if i == 2:
                rep = rep + "Free Blackthorn League: "
                if tup[i] is not None:
                    rep = rep + str(tup[i]) + "\n"
                else:
                    rep = rep + "\n"
                return rep
            rep = rep + "Peace Corps: "
            if tup[i] is not None:
                rep = rep + str(tup[i]) + "\n"
            else:
                rep = rep + "\n"
            return rep
