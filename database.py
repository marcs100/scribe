import sqlite3
from sqlite3 import *
import unicodedata
# import columns
from datetime import datetime


class database(object):
    def __init__(self, databaseFile):
        # self.dbFile= '/home/marc-pc/Documents/marcnotes_db'
        self.dbFile = databaseFile
        self.cursor = 0
        self.conn = None
        self.__connect()

    def close(self):
        self.cursor.close()

    def __connect(self):
        self.conn = sqlite3.connect(self.dbFile)  # @UndefinedVariable
        self.conn.execute('pragma foreign_keys=ON')
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()

    def commit(self):
        self.cursor = self.conn.cursor()

        self.conn.commit()

    # delete and notebookCovers entries that are no longer required
    def cleanNotebookCovers(self):
        self.cursor.execute("select distinct notebook from marcnotes")
        nBooks = self.cursor.fetchall()
        notebooksStr = ''
        for nb in nBooks:
            notebooksStr += "'" + nb[0] + "',"
        notebooksStr = notebooksStr[:len(notebooksStr) - 1]
        # print(notebooksStr)
        self.cursor.execute("delete from notebookCovers where name not in (" + notebooksStr + ")")
        self.commit()

    def deleteNotebook(self, notebook):
        dataTuple = (str(notebook),)
        self.cursor.execute("Delete from marcnotes where notebook = ?", dataTuple)
        self.commit()

    def deleteNotebookCover(self, notebook):
        dataTuple = (str(notebook),)
        self.cursor.execute("Delete from notebookCovers where name = ?", dataTuple)
        self.commit()

    def addNote(self, notebook, tag, contents, datestamp, pinnedStatus, backColour):
        dataTuple1 = (str(notebook), str(tag), str(contents),)
        dataTuple2 = (
        str(notebook), str(tag), str(contents), str(datestamp), str(datestamp), pinnedStatus, str(backColour),)
        # print(contents)
        # note we pass null for the first argument as id field will auto increment
        self.cursor.execute("select * from marcnotes where notebook = ? and tag = ? and content = ?", dataTuple1)
        row = self.cursor.fetchone()
        if row == None:
            self.cursor.execute("insert into marcnotes values (null,?,?,?,?,?,?,?)", dataTuple2)
            self.commit()
            self.cursor.execute("select last_insert_rowid() from marcnotes")
            rowid = self.cursor.fetchall()
            return rowid[0]
        else:
            print("notebook entry already exists!!!!!!!!!!")

    def addToNotebookCovers(self, notebook, colour):
        dataTuple = (str(notebook), str(colour))
        self.cursor.execute("insert into notebookCovers values (?,?)", dataTuple)
        self.commit()

    def updateNote(self, id, notebook, tag, contents, datecreated, pinnedStatus, backColour):
        # print('sqlid is '+str(id))
        dataTuple = (str(notebook), str(tag), str(contents), str(datecreated), pinnedStatus, str(backColour), id)
        # print('saving background colour'+backColour)
        self.cursor.execute(
            "update marcnotes set notebook = ?, tag = ?, content = ?, modified = ?, pinned = ?, BGColour = ? where id = ?",
            dataTuple)
        self.commit()

    def getNotebookNames(self):
        # self.cursor.execute("select distinct notebook from marcnotes order by notebook asc")
        self.cursor.execute("select name from notebookCovers order by name asc")
        rows = self.cursor.fetchall()
        return rows


    def getNumberOfSearchResults(self, searchQuery):

        searchTuple = (str('%' + searchQuery + '%'),)
        self.cursor.execute("select COUNT(*) from marcnotes where content like ? order by modified desc", searchTuple)

        rows = self.cursor.fetchall()
        return rows[0][0]

    # override - removing tag search until I can reimplemenent this in the UI better than before!!!
    def getSearchResults(self, searchQuery, resultsPerPage, startAt):

        searchTuple = (str('%' + searchQuery + '%'), str(resultsPerPage), str(startAt))
        self.cursor.execute(
            "select id, notebook, tag, substr(content,0,1800), created, modified, pinned, BGColour from marcnotes where content like ? order by modified desc LIMIT ? OFFSET ?",
            searchTuple)

        rows = self.cursor.fetchall()
        return rows

    def searchWholeWords(self, searchQuery):

        search_tuple = (str(searchQuery),)

        ''' THIS IS ONLY DONE ONCE _ SO NOT HERE!!!!!!!'''
        #self.cursor.execute("CREATE VIRTUAL TABLE search_table USING FTS5(id, content)")

        #delete existing content in search table
        self.cursor.execute("delete from search_table")
        self.commit()

        #get enetries to insert into virtual table
        records = self.cursor.execute(f"select id, content from marcnotes where content like '{searchQuery}'").fetchall()

        #add records to virtual table
        self.cursor.executemany("INSERT INTO search_table (id, content) VALUES(?,?)",records)
        self.commit()

        #NOTE: we can use AND/OR operator with match e.g. "where conent MATCH 'duck' OR content MATCH 'quack'"

        #run the search query on the virtual table
        query = f"select id, content from search_table where content MATCH '{searchQuery}'"
        print(query)
        self.cursor.execute(f"select id, content from search_table where content MATCH '{searchQuery}'")
        #self.cursor.execute("select id, content from search_table where content MATCH 'DoD'")
        results = self.cursor.fetchall()

        #delete existing content in search table
        self.cursor.execute("delete from search_table")
        self.commit()

        return results


    # return all notes that have been pinned
    def getPinnedNotes(self):
        # self.cursor.execute("select id, notebook, tag, content, BGColour from marcnotes where pinned is 1 order by modified desc")
        self.cursor.execute("select * from marcnotes where pinned is 1 order by modified desc")
        rows = self.cursor.fetchall()
        return rows

    def getNotebook(self, notebookName):
        self.cursor.execute(
            "select id, notebook, tag, substr(content,0,1800), created, modified, pinned, BGColour from marcnotes where notebook = ? order by modified desc",
            (notebookName,))
        rows = self.cursor.fetchall()
        return rows

    def getNumberOfNotesInNotebook(self, notebookName):
        self.cursor.execute("select COUNT(*) from marcnotes where notebook = ?", (notebookName,))
        rows = self.cursor.fetchall()
        return rows[0][0]

    def getNotebookPage(self, notebookName, resultsPerPage, startAt):
        # print('limit is '+str(resultsPerPage)+'\n') # debug only
        # print('offset is '+str(startAt)+'\n') # debug only
        paramTuple = (str(notebookName), str(resultsPerPage), str(startAt))
        self.cursor.execute(
            "select id, notebook, tag, substr(content,0,1800), created, modified, pinned, BGColour from marcnotes  where notebook = ? order by modified desc LIMIT ? OFFSET ?",
            paramTuple)
        rows = self.cursor.fetchall()
        return rows

    def getNoteByID(self, noteId):
        paramTuple = (str(noteId),)
        self.cursor.execute("select * from marcnotes where id = ?", paramTuple)
        rows = self.cursor.fetchall()
        return rows

    def deleteNoteById(self, noteId):
        paramTuple = (str(noteId),)
        self.cursor.execute("delete from marcnotes where id = ?", paramTuple)
        self.commit()

    def _getPinnedStatus(self, noteid):
        paramTuple = (str(noteid),)
        self.cursor.execute("select pinned from marcnotes where id = ?", paramTuple)
        row = self.cursor.fetchone()
        if row == None:
            return None
        else:
            return row[0]

    def togglePinnedStatus(self, noteid):
        paramTuple = (str(noteid),)
        if self._getPinnedStatus(noteid) == 1:
            self.cursor.execute("update marcnotes set pinned = 0 where id = ?", paramTuple)
        else:
            self.cursor.execute("update marcnotes set pinned = 1 where id = ?", paramTuple)
        self.commit()

    def getNotebookSqlIDs(self, notebook):
        paramTuple = (str(notebook),)
        self.cursor.execute("select id from marcnotes where notebook = ? order by id asc", paramTuple)
        rows = self.cursor.fetchall()
        return rows

    def getNotebookStats(self, notebook):
        paramTuple = (str(notebook),)
        self.cursor.execute("select COUNT(*) from marcnotes where notebook = ?", paramTuple)
        row = self.cursor.fetchone()
        return row[0]

    def getRecentNotes(self, numberOfNotes):
        paramTuple = (str(numberOfNotes),)
        self.cursor.execute("select * from marcnotes order by modified desc LIMIT ?", paramTuple)
        rows = self.cursor.fetchall()
        return rows

    def getNotebookColour(self, notebook):
        paramTuple = (str(notebook),)
        self.cursor.execute("select colour from notebookCovers where name = ?", paramTuple)
        row = self.cursor.fetchone()
        return row[0]

    def setNotebookColour(self, notebook, colour):
        paramTuple = (str(notebook), str(colour), str(notebook))
        self.cursor.execute("update notebookCovers set name = ?, colour = ? where name = ?", paramTuple)
        self.commit()
