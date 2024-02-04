
#Initialise empty list (this is probably not very pythonic!)
opened_notes = []


#------------------------------------------------------
# Return True if not is not already opned (in the list)
# then add not top the list
#
# Return False if note is aledy open (in the list)
#-----------------------------------------------------
def track_note(sqlid):
    global opened_notes
    if sqlid not in opened_notes:
        opened_notes.append(sqlid) # keep track of opened notes
        return True
    else:
        print(f"note {str(sqlid)} is already open")
        return False

#---------------------------------------------
# Return a list of all the currenly opn notes
#---------------------------------------------
def get_opened_notes():
    return opened_notes


#---------------------------------------------
# Check list contains a note and remove
# it if it does.
#---------------------------------------------
def delete_note(sqlid):
    if sqlid in opened_notes:
        opened_notes.remove(sqlid)
