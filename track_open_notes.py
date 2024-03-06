
#Initialise empty list (this is probably not very pythonic!)
_opened_notes = []
_new_note_counter = 0


#------------------------------------------------------
# Return True if not is not already opned (in the list)
# then add not top the list
#
# Return False if note is aledy open (in the list)
#-----------------------------------------------------
def track_note(sqlid):
    global opened_notes
    if sqlid not in _opened_notes:
        _opened_notes.append(sqlid) # keep track of opened notes
        return True
    else:
        print(f"note {str(sqlid)} is already open")
        return False

#---------------------------------------------
# Keep counter of opened new notes, that have
# not yet been saved.
#---------------------------------------------
def track_new_note():
    global _new_note_counter
    _new_note_counter += 1


#---------------------------------------------
# Decrement new note counter
# This shoudl be decremented when a new note
# has been saved.
#---------------------------------------------
def delete_new_note():
    global _new_note_counter
    if _new_note_counter > 0:
        _new_note_counter -= 1


#------------------------------------------------
# Return a counter to indicate how many new notes
# are opened that have not yet been saved.
#------------------------------------------------
def get_new_note_count():
    return _new_note_counter


#---------------------------------------------
# Return a list of all the currenly opn notes
#---------------------------------------------
def get_opened_notes():
    return _opened_notes


#---------------------------------------------
# Check if list contains a note and remove
# it if it does.
#---------------------------------------------
def delete_note(sqlid):
    if sqlid in _opened_notes:
        _opened_notes.remove(sqlid)
