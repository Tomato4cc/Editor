# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import shutil
from struct import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from ui.ui import Ui_Editor
from ui.player import Ui_Player

class PlayerItem(QListWidgetItem):
    def __init__(self, player=None):
        super().__init__()
        self.player = player
        
class PlayerTableItem(QTableWidgetItem):
    def __init__(self, player=None):
        super().__init__()
        self.player = player
        
class TeamTableItem(QTableWidgetItem):
    def __init__(self, team=None):
        super().__init__()
        self.team = team

class Player(QMainWindow, Ui_Player):
    def __init__(self, parent, player):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon('img/icon.png'))
        self.player = player
        self.parent = parent
        self.skill = 0
        self.com = 0  

        #Connect signals
        self.pcancel.clicked.connect(self.cancel)
        self.pacancel.clicked.connect(self.cancel)
        self.paccept.clicked.connect(self.save)
        self.paaccept.clicked.connect(self.save)
        self.page.editingFinished.connect(lambda: self.restrict(self.page, 15, 50))
        self.page.textEdited.connect(self.checke)
        self.pheight.editingFinished.connect(lambda: self.restrict(self.pheight, 138, 210))
        self.pheight.textEdited.connect(self.checke)
        self.pweight.editingFinished.connect(lambda: self.restrict(self.pweight, 0, 0))
        self.pweight.textEdited.connect(self.checke)
        self.pboots.textEdited.connect(self.checke)
        self.pgkgloves.textEdited.connect(self.checke)
        self.makegold.clicked.connect(lambda: self.medal(99, Editor.full))
        self.makesilver.clicked.connect(lambda: self.medal(88, Editor.silver))
        self.makebronze.clicked.connect(lambda: self.medal(77, Editor.bronze))
        self.padplus.clicked.connect(lambda: self.adjust(0))
        self.padminus.clicked.connect(lambda: self.adjust(1))
        self.padequ.clicked.connect(lambda: self.adjust(2))
        self.pfpc.clicked.connect(self.fpc)
        self.ppset.clicked.connect(self.phys)
        
        #Disabled for now
        #self.tabWidget.currentChanged.connect(self.tabresize)
        
        #Keyboard shortcuts
        QShortcut(QKeySequence("Shift+Return"), self, self.save)
        QShortcut(QKeySequence("Escape"), self, self.cancel)
        
        for id, button in Ui_Player._PLAYABLES.items():
            button.clicked.connect(self.playable)
            
        for field in Ui_Player._STATS:
            field.editingFinished.connect(self.stat)
            field.textEdited.connect(self.checke)
            
        for box in Ui_Player._SKILLS:
            box.clicked.connect(self.cskill)
        
        for box in Ui_Player._COMSTYLES:
            box.clicked.connect(self.ccom)
        
        #Sloppy way to keep track of amount of player skills
        for i in range(28):
            if(self.player['playerskills'][i]):
                self.skill = self.skill + 1
        
        #Same sloppy way for COM styles
        for i in range(6):
            if(self.player['comstyles'][i]):
                self.com = self.com + 1
    
    #Store magic offsets for datablocks
    _PLAYEROFFSET = 124
    _TEAMOFFSET = 3948124
    _TEAMPLAYEROFFSET = 4652884
    
    #Set all the physique sliders with one button
    def phys(self):
        valid = 0
        str = self.ppsete.text()
        if(len(str) > 1):
            sign = str[0:1]
            rest = str[1:]
            if((sign.isdigit() or sign == "-" or sign == "+") and rest.isdigit()):
                valid = 1
        else:
            if(str.isdigit()):
                valid = 1
    
        if(valid == 1):
            val = int(self.ppsete.text())
            if(val < -7):
                val = -7
            elif(val > 7):
                val = 7
                
            self.pneckl.setValue(val)
            self.pnecks.setValue(val)
            self.pshoulderh.setValue(val)
            self.pshoulderw.setValue(val)
            self.pchestm.setValue(val)
            self.pwaists.setValue(val)
            self.parms.setValue(val)
            self.pthighs.setValue(val)
            self.pcalfs.setValue(val)
            self.plegl.setValue(val)
            self.parml.setValue(val)
            self.pheadw.setValue(val)
            self.pheadl.setValue(val)
            self.pheadd.setValue(val)
  
    #Set FPC settings
    def fpc(self):
        self.pskincol.setCurrentIndex(7)
        self.pboots.setText("38")
        self.pshirttail.setCurrentIndex(0)
        self.psocks.setCurrentIndex(2)
        self.pankletape.setChecked(0)
        self.pglasses.setCurrentIndex(0)
        self.pwristtape.setCurrentIndex(0)
        
        if(self.pregpos.currentIndex() == 0):
            self.pgkgloves.setText("12")
            self.psleeves.setCurrentIndex(1)
        else:
            self.psleeves.setCurrentIndex(2)
        
    #Resize window on tab change
    #Currently disabled, it works but I'm not sure if it's a good idea
    #so it's included but not enabled.
    def tabresize(self, index):
        '''if(index == 1):
            self.setMinimumSize(QSize(485, 610))
            self.setMaximumSize(QSize(485, 610))
            self.resize(485, 610)'''
        if(index == 99999):
            self.setMinimumSize(QSize(1110, 870))
            self.setMaximumSize(QSize(1110, 870))
            self.resize(1110, 870)
    
    #Close window on cancel press
    def cancel(self):
        self.close()
    
    #Process COM style checkbox changes
    def ccom(self):
        send = self.sender()
        if(send.isChecked() == 1):
            if(self.com < 4 or (self.com == 4 and send.isChecked() == 0)):
                self.com = self.com + 1
            else:
                self.com = self.com + 1
                for box in Ui_Player._COMSTYLES:
                    if(box.isChecked() == 0):
                        box.setEnabled(0)
        else:
            self.com = self.com - 1
            if(self.com < 10):
                for box in Ui_Player._COMSTYLES:
                    box.setEnabled(1)
        self.label_46.setText("COM Styles (" + str(self.com) + "/5)")
    
    #Process skill checkbox changes
    #TODO: cleanup?
    def cskill(self):
        send = self.sender()
        if(send.isChecked() == 1):
            if(self.skill < 9 or (self.skill == 9 and send.isChecked() == 0)):
                self.skill = self.skill + 1
            else:
                self.skill = self.skill + 1
                for box in Ui_Player._SKILLS:
                    if(box.isChecked() == 0):
                        box.setEnabled(0)
        else:
            self.skill = self.skill - 1
            if(self.skill < 10):
                for box in Ui_Player._SKILLS:
                    box.setEnabled(1)
        self.label_44.setText("Player Skills (" + str(self.skill) + "/10)")
    
    #Handle stat adjust buttons
    def adjust(self, mode):
        #0 for +, 1 for -, 2 for =
        if(self.padjust.text() != ""): #Make sure there's input
            val = int(self.padjust.text())
            for field in Ui_Player._STATS:
                if(mode == 0):
                    new = int(field.text()) + val
                elif(mode == 1):
                    new = int(field.text()) - val
                elif(mode == 2):
                    new = val
                    
                if(new < 40):
                    new = 40
                    
                if(new >= 99):
                    new = 99
                    pal = Editor.full
                elif(new >= 90):
                    pal = Editor.gold
                elif(new >= 80):
                    pal = Editor.silver
                elif(new >= 70):
                    pal = Editor.bronze
                else:
                    pal = Editor.nonmed
                    
                field.setText(str(new))
                field.setPalette(pal)
    
    #Handle medal buttons and set the stats/palette in one go
    def medal(self, stat, palette):
        for field in Ui_Player._STATS:
            field.setText(str(stat))
            field.setPalette(palette)
    
    #Make sure height, weight and age fall in the PES accepted ranges
    def restrict(self, source, mn, mx):
        if(mn == 0):
            mn = max(30, int(self.pheight.text())-129)
        if(mx == 0):
            mx = int(self.pheight.text())-81
        if(int(source.text()) < mn):
            source.setText(str(mn))
        if(int(source.text()) > mx):
            source.setText(str(mx))
            
        if(source == self.pheight):
            h = int(self.pheight.text())
            w = int(self.pweight.text())
            if(w < max(30, h-129)):
                self.pweight.setText(str(max(30, h-129)))
            elif(w > h-81):
                self.pweight.setText(str(h-81))
    
    #Make sure input fields have valid input and are not empty or too small
    def checke(self):
        send = self.sender()
        if(send.text() == ""):
            if(send == self.page):
                send.setText("15")
            elif(send == self.pweight):
                send.setText(str(max(30, int(self.pheight.text())-129)))
            elif(send == self.pheight):
                send.setText("138")
                h = 138
                w = int(self.pweight.text())
                if(w < max(30, h-129)):
                    self.pweight.setText(str(max(30, h-129)))
            elif(send == self.pboots or send == self.pgkgloves):
                send.setText("0")
            else:
                send.setText("40")
    
    #Make sure stats are not too low and set field palettes
    def stat(self):
        send = self.sender()
        val = int(send.text())
        if(val < 40 or send.text() == ""):
            send.setText("40")
            send.setPalette(Editor.nonmed)
        if(val < 70):
            send.setPalette(Editor.nonmed)
        elif(val >= 70 and val < 80):
            send.setPalette(Editor.bronze)
        elif(val >= 80 and val < 90):
            send.setPalette(Editor.silver)
        elif(val >= 90 and val < 99):
            send.setPalette(Editor.gold)
        elif(val == 99):
            send.setPalette(Editor.full)
    
    #Handle playable position buttons
    def playable(self):
        bt = self.sender()
        bid = 0
        for id, button in Ui_Player._PLAYABLES.items():
            if(button == bt):
                bid = id
        if(self.player['playables'][bid] == 0):
            bt.setStyleSheet("background-color: #FFFF00")
            self.player['playables'][bid] = 1
        elif(self.player['playables'][bid] == 1):
            bt.setStyleSheet("background-color: #FF0000")
            self.player['playables'][bid] = 2
        elif(self.player['playables'][bid] == 2):
            bt.setStyleSheet("")
            self.player['playables'][bid] = 0
    
    #Save the data for current player
    def save(self):
        b = open('out/data.dat', 'r+b')
        
        #First set the in-editor variables
        self.player['pid'] = int(self.pid.text())
        self.player['commid'] = int(self.pcommid.text())
        self.player['nationality'] = self.pnationality.currentData()
        self.player['height'] = int(self.pheight.text())
        self.player['weight'] = int(self.pweight.text())
        self.player['goal1'] = self.pgoalcel1.currentData()
        self.player['goal2'] = self.pgoalcel2.currentData()
        
        self.player['attprow'] = int(self.pattprow.text())
        self.player['defprow'] = int(self.pdefprow.text())
        self.player['goalkeeping'] = int(self.pgoalkeeping.text())
        self.player['dribbling'] = int(self.pdribbling.text())
        self.player['fkmotion'] = self.pfkmot.currentData()
        
        self.player['finishing'] = int(self.pfinishing.text())
        self.player['lowpass'] = int(self.plowpass.text())
        self.player['loftedpass'] = int(self.ploftedpass.text())
        self.player['header'] = int(self.pheader.text())
        self.player['form'] = self.pform.currentData()
        self.player['editedplayer'] = 1 #Reset flag
        
        self.player['swerve'] = int(self.pswerve.text())
        self.player['catching'] = int(self.pcatching.text())
        self.player['clearing'] = int(self.pclearing.text())
        self.player['reflexes'] = int(self.preflexes.text())
        self.player['injuryres'] = self.pinjuryres.currentData()
        self.player['editedbasic'] = 1 #Reset flag
        
        self.player['strball'] = int(self.pstrball.text())
        self.player['physical'] = int(self.pphyscont.text())
        self.player['kickingpower'] = int(self.pkickpower.text())
        self.player['explosivepower'] = int(self.pexplopower.text())
        self.player['dribblearmmotion'] = self.pdribarm.currentData()
        self.player['editedregpos'] = 1 #Reset flag
        
        self.player['age'] = int(self.page.text())
        self.player['regpos'] = self.pregpos.currentData()
        self.player['playstyle'] = self.pplayingstyle.currentData()
        
        self.player['ballcontrol'] = int(self.pballcontrol.text())
        self.player['ballwinning'] = int(self.pballwinning.text())
        self.player['wfacc'] = self.pwfacc.currentData()
        
        self.player['jump'] = int(self.pjump.text())
        self.player['runarmmotion'] = self.prunarm.currentData()
        self.player['ckmotion'] = self.pckmot.currentData()
        self.player['coverage'] = int(self.pcoverage.text())
        self.player['wfusage'] = self.pwfusage.currentData()
        
        self.player['dhunchmotion'] = self.pdribhunch.currentData()
        self.player['rhunchmotion'] = self.prunhunch.currentData()
        self.player['pkmotion'] = self.ppkmot.currentData()
        self.player['placekicking'] = int(self.pplacekicking.text())
        self.player['playposedited'] = 1 #Reset flag
        self.player['abilityedited'] = 1 #Reset flag
        self.player['skillsedited'] = 1 #Reset flag
        
        self.player['stamina'] = int(self.pstamina.text())
        self.player['speed'] = int(self.pspeed.text())
        self.player['playstyleedited'] = 1 #Reset flag
        self.player['comedited'] = 1 #Reset flag
        
        self.player['motionedited'] = 1 #Reset flag
        self.player['basecopy'] = 0 #Reset flag
        self.player['strfoot'] = self.pfooting.currentData()
        
        i = 0
        for box in Ui_Player._COMSTYLES:
            if(box.isChecked()):
                self.player['comstyles'][i] = 1
            else:
                self.player['comstyles'][i] = 0
            i = i + 1
        
        i = 0
        for box in Ui_Player._SKILLS:
            if(box.isChecked()):
                self.player['playerskills'][i] = 1
            else:
                self.player['playerskills'][i] = 0
            i = i + 1
        
        self.player['name'] = self.pname.text()
        self.player['print'] = self.pshirtname.text()
        
        self.player['facee'] = int(self.pfacee.isChecked())
        self.player['haire'] = int(self.phaire.isChecked())
        self.player['physe'] = int(self.pphyse.isChecked())
        self.player['stripe'] = int(self.pstripe.isChecked())
        self.player['boots'] = int(self.pboots.text())
        self.player['gkgloves'] = int(self.pgkgloves.text())
        
        self.player['skincolour'] = self.pskincol.currentData()
        
        self.player['glasses'] = self.pglasses.currentData()
        self.player['unders'] = self.pshorts.currentData()
        self.player['wtape'] = self.pwristtape.currentData()
        self.player['sleeves'] = self.psleeves.currentData()
        self.player['socks'] = self.psocks.currentData()
        self.player['shirttail'] = self.pshirttail.currentData()
        self.player['ankletape'] = int(self.pankletape.isChecked())
        
        self.player['neckl'] = self.pneckl.value() + 7
        self.player['necks'] = self.pnecks.value() + 7
        self.player['shoulderh'] = self.pshoulderh.value() + 7
        self.player['shoulderw'] = self.pshoulderw.value() + 7
        self.player['chestm'] = self.pchestm.value() + 7
        self.player['waists'] = self.pwaists.value() + 7
        self.player['arms'] = self.parms.value() + 7
        self.player['thighs'] = self.pthighs.value() + 7
        self.player['calfs'] = self.pcalfs.value() + 7
        self.player['legl'] = self.plegl.value() + 7
        self.player['arml'] = self.parml.value() + 7
        self.player['headl'] = self.pheadl.value() + 7
        self.player['headw'] = self.pheadw.value() + 7
        self.player['headd'] = self.pheadd.value() + 7
        
        #Then write to file
        b.seek(self._PLAYEROFFSET + self.player['findex']*188)
        b.write(pack('<I', self.player['pid']))
        if(self.player['commid'] == 0):
            b.write(pack('>I', 0xFFFFFFFF))
        else:
            b.write(pack('<I', self.player['commid']))
        b.seek(2, 1) #Skip unknown entry
        b.write(pack('<H', self.player['nationality']))
        b.write(pack('<B', self.player['height']))
        b.write(pack('<B', self.player['weight']))
        b.write(pack('<B', self.player['goal1']))
        b.write(pack('<B', self.player['goal2']))
        
        dat = self.player['attprow']
        dat |= self.player['defprow'] << 7
        dat |= self.player['goalkeeping'] << 14
        dat |= self.player['dribbling'] << 21
        dat |= self.player['fkmotion'] << 28
        b.write(pack('<I', dat))
        
        dat = self.player['finishing']
        dat |= self.player['lowpass'] << 7
        dat |= self.player['loftedpass'] << 14
        dat |= self.player['header'] << 21
        dat |= self.player['form'] << 28
        dat |= self.player['editedplayer'] << 31
        b.write(pack('<I', dat))
        
        dat = self.player['swerve']
        dat |= self.player['catching'] << 7
        dat |= self.player['clearing'] << 14
        dat |= self.player['reflexes'] << 21
        dat |= self.player['injuryres'] << 28
        dat |= self.player['unknownb'] << 30
        dat |= self.player['editedbasic'] << 31
        b.write(pack('<I', dat))
        
        dat = self.player['strball']
        dat |= self.player['physical'] << 7
        dat |= self.player['kickingpower'] << 14
        dat |= self.player['explosivepower'] << 21
        dat |= self.player['unknownmotion'] << 28
        dat |= self.player['editedregpos'] << 31
        b.write(pack('<I', dat))
        
        dat = self.player['age']
        dat |= self.player['regpos'] << 6
        dat |= self.player['unknownc'] << 10
        dat |= self.player['playstyle'] << 11
        b.write(pack('<H', dat))
        
        dat = self.player['ballcontrol']
        dat |= self.player['ballwinning'] << 7
        dat |= self.player['wfacc'] << 14
        b.write(pack('<H', dat))
        
        dat = self.player['jump']
        dat |= self.player['dribblearmmotion'] << 7
        dat |= self.player['runarmmotion'] << 10
        dat |= self.player['ckmotion'] << 13
        dat |= self.player['coverage'] << 16
        dat |= self.player['wfusage'] << 23
        dat |= self.player['playables'][0] << 25
        dat |= self.player['playables'][1] << 27
        dat |= self.player['playables'][2] << 29
        dat |= self.player['playposedited'] << 31

        b.write(pack('<I', dat))
        
        dat = self.player['playables'][4]
        dat |= self.player['playables'][5] << 2
        dat |= self.player['playables'][6] << 4
        dat |= self.player['playables'][7] << 6
        dat |= self.player['playables'][8] << 8
        dat |= self.player['playables'][9] << 10
        dat |= self.player['playables'][10] << 12
        dat |= self.player['playables'][11] << 14
        
        b.write(pack('<H', dat))
        
        dat = self.player['playables'][12]
        dat |= self.player['dhunchmotion'] << 2
        dat |= self.player['rhunchmotion'] << 4
        dat |= self.player['pkmotion'] << 6
        b.write(pack('<B', dat))
        
        dat = self.player['placekicking']
        dat |= self.player['abilityedited'] << 7
        b.write(pack('<B', dat))
        
        dat = self.player['stamina']
        dat |= self.player['playables'][3] << 7
        dat |= self.player['speed'] << 9
        b.write(pack('<H', dat))
        
        dat = self.player['skillsedited']
        dat |= self.player['playstyleedited'] << 1
        dat |= self.player['comedited'] << 2
        dat = self.player['motionedited'] << 3
        dat |= self.player['basecopy'] << 4
        dat |= self.player['unknownd'] << 5
        dat |= self.player['strfoot'] << 6
        dat |= self.player['unknowne'] << 7
        b.write(pack('<B', dat))
        
        dat = self.player['comstyles'][0]
        dat |= self.player['comstyles'][1] << 1
        dat |= self.player['comstyles'][2] << 2
        dat |= self.player['comstyles'][3] << 3
        dat |= self.player['comstyles'][4] << 4
        dat |= self.player['comstyles'][5] << 5
        dat |= self.player['comstyles'][6] << 6
        dat |= self.player['playerskills'][0] << 7
        dat |= self.player['playerskills'][1] << 8
        dat |= self.player['playerskills'][2] << 9
        dat |= self.player['playerskills'][3] << 10
        dat |= self.player['playerskills'][4] << 11
        dat |= self.player['playerskills'][5] << 12
        dat |= self.player['playerskills'][6] << 13
        dat |= self.player['playerskills'][7] << 14
        dat |= self.player['playerskills'][8] << 15
        b.write(pack('<H', dat))
        
        dat = self.player['playerskills'][9]
        dat |= self.player['playerskills'][10] << 1
        dat |= self.player['playerskills'][11] << 2
        dat |= self.player['playerskills'][12] << 3
        dat |= self.player['playerskills'][13] << 4
        dat |= self.player['playerskills'][14] << 5
        dat |= self.player['playerskills'][15] << 6
        dat |= self.player['playerskills'][16] << 7
        b.write(pack('<B', dat))
        
        dat = self.player['playerskills'][17]
        dat |= self.player['playerskills'][18] << 1
        dat |= self.player['playerskills'][19] << 2
        dat |= self.player['playerskills'][20] << 3
        dat |= self.player['playerskills'][21] << 4
        dat |= self.player['playerskills'][22] << 5
        dat |= self.player['playerskills'][23] << 6
        dat |= self.player['playerskills'][24] << 7
        b.write(pack('<B', dat))  
        
        dat = self.player['playerskills'][25]
        dat |= self.player['playerskills'][26] << 1
        dat |= self.player['playerskills'][27] << 2
        dat |= self.player['unknownblock'] << 3
        b.write(pack('<B', dat))

        na = self.player['name'].encode('utf-8')[:45]
        #Terrible way of limiting amount of bytes in string with multi-byte characters, but it werks
        na = na.decode('utf-8', errors='ignore')
        na = na.encode('utf-8')
        pr = self.player['print'].upper().encode('utf-8')[:17]
        pr = pr.decode('utf-8', errors='ignore')
        pr = pr.encode('utf-8')
        b.write(pack("%ds%dx" % (len(na), 46-len(na)), na))
        b.write(pack("%ds%dx" % (len(pr), 18-len(pr)), pr))
        
        b.seek(4, 1)
        dat = self.player['facee']
        dat |= self.player['haire'] << 1
        dat |= self.player['physe'] << 2
        dat |= self.player['stripe'] << 3
        dat |= self.player['boots'] << 4
        dat |= self.player['gkgloves'] << 18
        dat |= self.player['appunknownb'] << 28
        b.write(pack('<I', dat))
        
        b.seek(4, 1)
        
        dat = self.player['neckl']
        dat |= self.player['necks'] << 4
        dat |= self.player['shoulderh'] << 8
        dat |= self.player['shoulderw'] << 12
        dat |= self.player['chestm'] << 16
        dat |= self.player['waists'] << 20
        dat |= self.player['arms'] << 24
        dat |= self.player['arml'] << 28
        b.write(pack('<I', dat))
        
        dat = self.player['thighs']
        dat |= self.player['calfs'] << 4
        dat |= self.player['legl'] << 8
        dat |= self.player['headl'] << 12
        dat |= self.player['headw'] << 16
        dat |= self.player['headd'] << 20
        dat |= self.player['wtapeextra'] << 24
        dat |= self.player['wtape'] << 30
        b.write(pack('<I', dat))

        dat = self.player['glassescol']
        dat |= self.player['glasses'] << 3
        dat |= self.player['sleeves'] << 6
        dat |= self.player['inners'] << 8
        dat |= self.player['socks'] << 10
        dat |= self.player['unders'] << 12
        dat |= self.player['shirttail'] << 14
        dat |= self.player['ankletape'] << 15
        b.write(pack('<H', dat))
        
        b.seek(23, 1)
        dat = self.player['skincolour']
        dat |= self.player['appunknownf'] << 3
        b.write(pack('<B', dat))
        
        b.seek(26, 1)
        
        b.close()
        
        Editor.players[self.player['pid']] = self.player #Write in-editor variables to main dictionary
        Editor.saved = 1 #Set flag for exit confirm
        Editor.playup(self.parent, self.player['pid']) #Let Editor class handle things like current selected player and list status
        
        self.close() #Done, close window
        
class Editor(QMainWindow, Ui_Editor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon('img/icon.png'))
        
        #Connect menu signals
        self.actionLOAD_OF.triggered.connect(self.from_edit)
        self.actionSave.triggered.connect(lambda: self.save(0))
        self.actionSave_As.triggered.connect(lambda: self.save(1))
        self.actionExit.triggered.connect(self.closef)
        
        #Connect signals
        self.teamDropdown1.currentIndexChanged.connect(lambda: self.playerlist(self.teamPlayerList1, self.teams[self.teamDropdown1.currentData()], self.players))
        self.teamDropdown2.currentIndexChanged.connect(lambda: self.playerlist(self.teamPlayerList2, self.teams[self.teamDropdown2.currentData()], self.players))
        
        self.teamPlayerList1.itemSelectionChanged.connect(lambda: self.player(self.players[self.teamPlayerList1.currentItem().player]))
        self.teamPlayerList2.itemSelectionChanged.connect(lambda: self.player(self.players[self.teamPlayerList2.currentItem().player]))
        self.teamPlayerList1.cellDoubleClicked.connect(lambda: self.editp(self.players[self.teamPlayerList1.currentItem().player]))
        self.teamPlayerList2.cellDoubleClicked.connect(lambda: self.editp(self.players[self.teamPlayerList2.currentItem().player]))
        self.teamPlayerList1.enterPressed.connect(lambda: self.editp(self.players[self.teamPlayerList1.currentItem().player]))
        self.teamPlayerList2.enterPressed.connect(lambda: self.editp(self.players[self.teamPlayerList2.currentItem().player]))
        
        self.teamTable.itemSelectionChanged.connect(self.team)
        
        self.playerList.itemSelectionChanged.connect(lambda: self.player(self.players[self.playerList.currentItem().player]))
        self.playerList.enterPressed.connect(lambda: self.editp(self.players[self.playerList.currentItem().player]))
        self.playerList.itemDoubleClicked.connect(lambda: self.editp(self.players[self.playerList.currentItem().player]))
        
        self.resflags.clicked.connect(self.flags)
        self.restflags.clicked.connect(self.tflags)
        self.resbcopy.clicked.connect(self.bcopy)
        self.taccept.clicked.connect(self.saveteam)
        
        self.ptsetfpc.clicked.connect(self.setfpc)
        self.ptrestp.clicked.connect(self.restfpc)
        
        #Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+S"), self, lambda: self.save(0))
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, lambda: self.save(1))
    
    skillcount = 0 #Amount of skills
    comcount = 0 #Amount of COM styles
    players = {} #Main player dictionary
    teams = {} #Main team dictionary
    saved = 0 #Flag for exit confirm, set if a player has been edited
    loaded = 0 #Flag to check if EDIT data has been loaded
    efile = None #Location of EDIT file
    opath = os.path.expanduser('~/Documents/KONAMI/Pro Evolution Soccer 2017/save/') #Default path for PES save folder
    
    #Store magic offsets for datablocks
    _PLAYEROFFSET = 124
    _TEAMOFFSET = 3948124
    _TEAMPLAYEROFFSET = 4652884
    _TEAMCOUNTOFFSET = 100
    _PLAYERCOUNTOFFSET = 96
    
    #Check if saved savepath file exists and use it if it does
    if(os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tdata.txt'))):
        ob = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tdata.txt'), 'r')
        opath = ob.read()
        ob.close()
    
    #Set palettes for different stats
    nonmed = QPalette()
    nonmed.setColor(9, QColor(255, 255, 255, 255));
    bronze = QPalette()
    bronze.setColor(9, QColor(173, 255, 47, 255));
    silver = QPalette()
    silver.setColor(9, QColor(255, 255, 0, 255));
    gold = QPalette()
    gold.setColor(9, QColor(255, 165, 0, 255));
    full = QPalette()
    full.setColor(9, QColor(255, 0, 0, 255));
    
    #Store possible player positions in convenient dict
    _POSLIST = {0:"GK", 1:"CB", 2:"LB", 3:"RB", 4:"DMF", 5:"CMF", 6:"LMF", 7:"RMF", 8:"AMF", 9:"LWF", 10:"RWF", 11:"SS", 12:"CF"}
    
    #Load player data from EDIT, populate dicts, fill player lists, generally just do everything
    def from_edit(self):
        f = QFileDialog.getOpenFileName(self, 'Edit File', self.opath, "")
        if(f[0].replace(" ", "") != ""):
            ob = open('tdata.txt', 'w')
            ob.write(f[0])
            ob.close()
            if(os.path.exists('out')):
                shutil.rmtree('out')
            subprocess.call(['lib/decrypter18.exe', f[0], 'out'])
            self.efile = f[0]
            if(os.path.exists('out')):
                b = open('out/data.dat', 'rb')
                
                #Process teams
                b.seek(self._TEAMCOUNTOFFSET)
                tc = unpack('<H', b.read(2))[0]
                for i in range(tc):
                    b.seek(self._TEAMOFFSET + (i)*480)
                    tl = {}
                    tid = unpack('<I', b.read(4))[0]
                    b.seek(148, 1)
                    tn = b.read(70).decode('utf-8').rstrip(' \t\r\n\0')
                    tsn = b.read(125).decode('utf-8').rstrip(' \t\r\n\0')
                    
                    b.seek(self._TEAMPLAYEROFFSET + (i)*164)
                    b.seek(4, 1)
                    players = []
                    for j in range(32):
                        pid = unpack('<I', b.read(4))[0]
                        if(pid != 0):
                            players.append(pid)
                            
                    b.seek(self._TEAMPLAYEROFFSET + (i)*164)
                    b.seek(132, 1)
                    nums = []
                    for j in range(len(players)):
                        num = unpack('<B', b.read(1))[0]
                        nums.append(num)
                    
                    tl['name'] = tn
                    tl['short'] = tsn
                    tl['players'] = players
                    tl['nums'] = nums
                    tl['tid'] = tid
                    tl['tindex'] = i
                    self.teams[tid] = tl
                print(len(self.teams))
                    
                #Process players
                b.seek(self._PLAYERCOUNTOFFSET)
                pc = unpack('<H', b.read(2))[0]
                b.seek(self._PLAYEROFFSET)
                for i in range(pc):
                    pid = unpack('<I', b.read(4))[0]
                    pdata = {}
                    playables = {}
                    playerskills = {}
                    comstyles = {}
                    
                    pdata['pid'] = pid
                    pdata['commid'] = unpack('<I', b.read(4))[0]
                    b.seek(2, 1) #Skip unknown entry
                    pdata['nationality'] = unpack('<H', b.read(2))[0]
                    if(pdata['nationality'] == 0):
                        pdata['nationality'] = 231
                    pdata['height'] = unpack('<B', b.read(1))[0]
                    pdata['weight'] = unpack('<B', b.read(1))[0]
                    pdata['goal1'] = unpack('<B', b.read(1))[0]
                    pdata['goal2'] = unpack('<B', b.read(1))[0]
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['attprow'] = (dat & 0b1111111)
                    pdata['defprow'] = (dat >> 7 & 0b1111111)
                    pdata['goalkeeping'] = (dat >> 14 & 0b1111111)
                    pdata['dribbling'] = (dat >> 21 & 0b1111111)
                    pdata['fkmotion'] = (dat >> 28 & 0b1111)
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['finishing'] = (dat & 0b1111111)
                    pdata['lowpass'] = (dat >> 7 & 0b1111111)
                    pdata['loftedpass'] = (dat >> 14 & 0b1111111)
                    pdata['header'] = (dat >> 21 & 0b1111111)
                    pdata['form'] = (dat >> 28 & 0b111)
                    pdata['editedplayer'] = (dat >> 31 & 0b1)
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['swerve'] = (dat & 0b1111111)
                    pdata['catching'] = (dat >> 7 & 0b1111111)
                    pdata['clearing'] = (dat >> 14 & 0b1111111)
                    pdata['reflexes'] = (dat >> 21 & 0b1111111)
                    pdata['injuryres'] = (dat >> 28 & 0b11)
                    pdata['unknownb'] = (dat >> 30 & 0b1)
                    pdata['editedbasic'] = (dat >> 31 & 0b1)
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['strball'] = (dat & 0b1111111)
                    pdata['physical'] = (dat >> 7 & 0b1111111)
                    pdata['kickingpower'] = (dat >> 14 & 0b1111111)
                    pdata['explosivepower'] = (dat >> 21 & 0b1111111)
                    #This looks like a motion but not sure if it's used
                    pdata['unknownmotion'] = (dat >> 28 & 0b111)
                    pdata['editedregpos'] = (dat >> 31 & 0b1)
                    
                    dat = unpack('<H', b.read(2))[0]
                    pdata['age'] = (dat & 0b111111)
                    pdata['regpos'] = (dat >> 6 & 0b1111)
                    pdata['unknownc'] = (dat >> 10 & 0b1)
                    pdata['playstyle'] = (dat >> 11 & 0b11111)
                    
                    dat = unpack('<H', b.read(2))[0]
                    pdata['ballcontrol'] = (dat & 0b1111111)
                    pdata['ballwinning'] = (dat >> 7 & 0b1111111)
                    pdata['wfacc'] = (dat >> 14 & 0b11)
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['jump'] = (dat & 0b1111111)
                    pdata['dribblearmmotion'] = (dat >> 7 & 0b111)
                    pdata['runarmmotion'] = (dat >> 10 & 0b111)
                    pdata['ckmotion'] = (dat >> 13 & 0b111)
                    pdata['coverage'] = (dat >> 16 & 0b1111111)
                    pdata['wfusage'] = (dat >> 23 & 0b11)
                    #Playables: CF SS LWF RWF AMF DMF CMF LMF RMF CB LB RB GK
                    playables[0] = (dat >> 25 & 0b11)
                    playables[1] = (dat >> 27 & 0b11)
                    playables[2] = (dat >> 29 & 0b11)
                    pdata['playposedited'] = (dat >> 31 & 0b1)
                    
                    dat = unpack('<I', b.read(4))[0]
                    playables[4] = (dat & 0b11)
                    playables[5] = (dat >> 2 & 0b11)
                    playables[6] = (dat >> 4 & 0b11)
                    playables[7] = (dat >> 6 & 0b11)
                    playables[8] = (dat >> 8 & 0b11)
                    playables[9] = (dat >> 10 & 0b11)
                    playables[10] = (dat >> 12 & 0b11)
                    playables[11] = (dat >> 14 & 0b11)
                    playables[12] = (dat >> 16 & 0b11)
                    pdata['dhunchmotion'] = (dat >> 18 & 0b11)
                    pdata['rhunchmotion'] = (dat >> 20 & 0b11)
                    pdata['pkmotion'] = (dat >> 22 & 0b11)
                    pdata['placekicking'] = (dat >> 24 & 0b1111111)
                    pdata['abilityedited'] = (dat >> 31 & 0b1)
                    
                    dat = unpack('<H', b.read(2))[0]
                    pdata['stamina'] = (dat & 0b1111111)
                    playables[3] = (dat >> 7 & 0b11)
                    pdata['speed'] = (dat >> 9 & 0b1111111)
                    
                    pdata['playables'] = playables
                    
                    dat = unpack('<B', b.read(1))[0]
                    pdata['skillsedited'] = (dat & 0b1)
                    pdata['playstyleedited'] = (dat >> 1 & 0b1)
                    pdata['comedited'] = (dat >> 2 & 0b1)
                    pdata['motionedited'] = (dat >> 3 & 0b1)
                    pdata['basecopy'] = (dat >> 4 & 0b1)
                    pdata['unknownd'] = (dat >> 5 & 0b1)
                    pdata['strfoot'] = (dat >> 6 & 0b1)
                    pdata['unknowne'] = (dat >> 7 & 0b1)
                    
                    dat = unpack('<I', b.read(4))[0]
                    #COM Styles: trickster mazerun speedbullet incisiverun lbexpert earlycross longranger
                    comstyles[0] = (dat & 0b1)
                    comstyles[1] = (dat >> 1 & 0b1)
                    comstyles[2] = (dat >> 2 & 0b1)
                    comstyles[3] = (dat >> 3 & 0b1)
                    comstyles[4] = (dat >> 4 & 0b1)
                    comstyles[5] = (dat >> 5 & 0b1)
                    comstyles[6] = (dat >> 6 & 0b1)
                    
                    pdata['comstyles'] = comstyles
                    
                    #Player Skills: scissors flipflap marseille sombrero cutbehind scotch heading lrd knuckle acrofinish heeltrick ftp otp weightpass pinpoint curler rabona lowlofted lowpunt longthrow gklongthrow malicia manmark trackback acroclear captaincy supersub fightspirit
                    playerskills[0] = (dat >> 7 & 0b1)
                    playerskills[1] = (dat >> 8 & 0b1)
                    playerskills[2] = (dat >> 9 & 0b1)
                    playerskills[3] = (dat >> 10 & 0b1)
                    playerskills[4] = (dat >> 11 & 0b1)
                    playerskills[5] = (dat >> 12 & 0b1)
                    playerskills[6] = (dat >> 13 & 0b1)
                    playerskills[7] = (dat >> 14 & 0b1)
                    playerskills[8] = (dat >> 15 & 0b1)
                    playerskills[9] = (dat >> 16 & 0b1)
                    playerskills[10] = (dat >> 17 & 0b1)
                    playerskills[11] = (dat >> 18 & 0b1)
                    playerskills[12] = (dat >> 19 & 0b1)
                    playerskills[13] = (dat >> 20 & 0b1)
                    playerskills[14] = (dat >> 21 & 0b1)
                    playerskills[15] = (dat >> 22 & 0b1)
                    playerskills[16] = (dat >> 23 & 0b1)
                    playerskills[17] = (dat >> 24 & 0b1)
                    playerskills[18] = (dat >> 25 & 0b1)
                    playerskills[19] = (dat >> 26 & 0b1)
                    playerskills[20] = (dat >> 27 & 0b1)
                    playerskills[21] = (dat >> 28 & 0b1)
                    playerskills[22] = (dat >> 29 & 0b1)
                    playerskills[23] = (dat >> 30 & 0b1)
                    playerskills[24] = (dat >> 31 & 0b1)
                    
                    dat = unpack('<B', b.read(1))[0]
                    playerskills[25] = (dat & 0b1)
                    playerskills[26] = (dat >> 1 & 0b1)
                    playerskills[27] = (dat >> 2 & 0b1)
                    pdata['unknownblock'] = (dat >> 3 & 0b11111)
                    
                    pdata['playerskills'] = playerskills
                    
                    pdata['name'] = b.read(46).decode('utf-8', errors='ignore').rstrip(' \t\r\n\0')
                    pdata['print'] = b.read(18).replace(b'\xfe', b'').decode('utf-8', errors='ignore').rstrip(' \t\r\n\0')
                    
                    b.seek(4, 1)
                    dat = unpack('<I', b.read(4))[0]
                    pdata['facee'] = (dat & 0b1)
                    pdata['haire'] = (dat >> 1 & 0b1)
                    pdata['physe'] = (dat >> 2 & 0b1)
                    pdata['stripe'] = (dat >> 3 & 0b1)
                    pdata['boots'] = (dat >> 4 & 0b11111111111111)
                    pdata['gkgloves'] = (dat >> 18 & 0b1111111111)
                    pdata['appunknownb'] = (dat >> 28 & 0b1111)
                    
                    b.seek(4, 1)
                    dat = unpack('<I', b.read(4))[0]
                    pdata['neckl'] = (dat & 0b1111)
                    pdata['necks'] = (dat >> 4 & 0b1111)
                    pdata['shoulderh'] = (dat >> 8 & 0b1111)
                    pdata['shoulderw'] = (dat >> 12 & 0b1111)
                    pdata['chestm'] = (dat >> 16 & 0b1111)
                    pdata['waists'] = (dat >> 20 & 0b1111)
                    pdata['arms'] = (dat >> 24 & 0b1111)
                    pdata['arml'] = (dat >> 28 & 0b1111)
                    
                    dat = unpack('<I', b.read(4))[0]
                    pdata['thighs'] = (dat & 0b1111)
                    pdata['calfs'] = (dat >> 4 & 0b1111)
                    pdata['legl'] = (dat >> 8 & 0b1111)
                    pdata['headl'] = (dat >> 12 & 0b1111)
                    pdata['headw'] = (dat >> 16 & 0b1111)
                    pdata['headd'] = (dat >> 20 & 0b1111)
                    pdata['wtapeextra'] = (dat >> 24 & 0b111111)
                    pdata['wtape'] = (dat >> 30 & 0b11)
                    
                    dat = unpack('<H', b.read(2))[0]
                    pdata['glassescol'] = (dat & 0b111)
                    pdata['glasses'] = (dat >> 3 & 0b111)
                    pdata['sleeves'] = (dat >> 6 & 0b11)
                    pdata['inners'] = (dat >> 8 & 0b11)
                    pdata['socks'] = (dat >> 10 & 0b11)
                    pdata['unders'] = (dat >> 12 & 0b11)
                    pdata['shirttail'] = (dat >> 14 & 0b1)
                    pdata['ankletape'] = (dat >> 15 & 0b1)
                    
                    b.seek(23, 1)
                    dat = unpack('<B', b.read(1))[0]
                    pdata['skincolour'] = (dat & 0b111)
                    pdata['appunknownf'] = (dat >> 3 & 0b11111)
                    
                    #TODO: find a better way to do this
                    for tid, tdata in self.teams.items():
                        if(pdata['pid'] in tdata['players']):
                            pdata['tid'] = tid
                    
                    pdata['findex'] = i
                    
                    b.seek(26, 1)
                    
                    self.players[pid] = pdata
                
                b.close()
                
                #Fill player list in GUI
                print(len(self.players))
                self.playerList.clear()
                for id, data in sorted(self.players.items()):
                    item = PlayerItem()
                    item.player = id
                    item.setText(data['name'])
                    self.playerList.addItem(item)
                    
                #Fill team list in GUI
                i = 0
                self.teamTable.clearContents()
                self.teamTable.setRowCount(0)
                for id, data in sorted(self.teams.items()):
                    list = self.teamTable
                    list.insertRow(i)
            
                    item = TeamTableItem()
                    item.team = id
                    item.setText(str(data['tid']))
                    list.setItem(i, 0, item)
                    
                    item = TeamTableItem()
                    item.team = id
                    item.setText(data['short'])
                    list.setItem(i, 1, item)
                    
                    item = TeamTableItem()
                    item.team = id
                    item.setText(data['name'])
                    list.setItem(i, 2, item)
                    i = i + 1
                    
                #Fill team dropdowns
                self.teamDropdown1.blockSignals(1)
                self.teamDropdown2.blockSignals(1)
                self.teamDropdown1.clear()
                self.teamDropdown2.clear()
                for tid, tdata in self.teams.items():
                    self.teamDropdown1.addItem(tdata['name'], tid)
                    self.teamDropdown2.addItem(tdata['name'], tid)
                self.teamDropdown1.setCurrentIndex(0)
                self.teamDropdown2.setCurrentIndex(0)
                self.teamDropdown1.blockSignals(0)
                self.teamDropdown2.blockSignals(0)
                    
                #Manually fire changed signal on team player tables
                self.playerlist(self.teamPlayerList1, self.teams[self.teamDropdown1.currentData()], self.players)
                self.playerlist(self.teamPlayerList2, self.teams[self.teamDropdown2.currentData()], self.players)
                
                #Manually set selected player
                self.player(self.players[self.teamPlayerList1.currentItem().player])
                
                #Set loaded flag
                self.loaded = 1
    
    def team(self):
        team = self.teams[self.teamTable.currentItem().team]
        
        self.tname.setText(team['name'])
        self.tshort.setText(team['short'])
        
    def saveteam(self):
        if(self.loaded == 1):
            #First move unsaved changes to main team dictionary
            team = self.teamTable.currentItem().team
            
            self.teams[team]['name'] = self.tname.text()
            self.teams[team]['short'] = self.tshort.text()
            
            row = self.teamTable.currentItem().row()
            self.teamTable.item(row, 1).setText(self.teams[team]['short'])
            self.teamTable.item(row, 2).setText(self.teams[team]['name'])
            self.teamDropdown1.setItemText(row, self.teams[team]['name'])
            self.teamDropdown2.setItemText(row, self.teams[team]['name'])
            
            #Then save changes to file
            b = open('out/data.dat', 'r+b')
            b.seek(self._TEAMOFFSET + self.teams[team]['tindex']*480) #Skip to correct entry
            b.seek(152, 1) #Skip to name field
            
            na = self.tname.text().encode('utf-8')[:69]
            #Terrible way of limiting amount of bytes in string with multi-byte characters, but it werks
            na = na.decode('utf-8', errors='ignore')
            na = na.encode('utf-8')
            sh = self.tshort.text().encode('utf-8')[:3]
            sh = sh.decode('utf-8', errors='ignore')
            sh = sh.encode('utf-8')
            b.write(pack("%ds%dx" % (len(na), 70-len(na)), na))
            b.write(pack("%ds%dx" % (len(sh), 3-len(sh)), sh))
            
            b.close()
    
    def playerlist(self, list, team, players):
        self.teamPlayerList1.blockSignals(1)
        self.teamPlayerList2.blockSignals(1)
        list.setRowCount(0)
        pl = team['players']
        i = 0
        for player in pl:
            nr = team['nums'][i]
            name = players[player]['name']
            pos = self._POSLIST[players[player]['regpos']]
            
            list.insertRow(i)
            
            item = PlayerTableItem()
            item.player = player
            item.setText(pos)
            list.setItem(i, 0, item)
            
            item = PlayerTableItem()
            item.player = player
            item.setText(name)
            list.setItem(i, 1, item)
            
            item = PlayerTableItem()
            item.player = player
            item.setText(str(nr))
            list.setItem(i, 2, item)
            
            i = i + 1
        self.teamPlayerList1.blockSignals(0)
        self.teamPlayerList2.blockSignals(0)
        list.setCurrentCell(0, 1)
    
    def playup(self, pid):
        if(self.teamPlayerList2.currentItem().player == pid):
            self.playerlist(self.teamPlayerList1, self.teams[self.teamDropdown1.currentData()], self.players)
            self.playerlist(self.teamPlayerList2, self.teams[self.teamDropdown2.currentData()], self.players)
        else:
            self.playerlist(self.teamPlayerList2, self.teams[self.teamDropdown2.currentData()], self.players)
            self.playerlist(self.teamPlayerList1, self.teams[self.teamDropdown1.currentData()], self.players)
        self.player(self.players[pid])
    
    def player(self, player):
        #list.clearContents() also fires a signal that returns a nonexistent ID, handle that
        team = self.teams[player['tid']]
        if(player['pid'] in team['players']):
            self.pname.setText(str(player['name']))
            self.shirtname.setText(str(player['print']))
            self.commid.setText(str(player['commid']))
            self.number.setText(str(team['nums'][team['players'].index(player['pid'])]))
            self.club.setText(str(team['name']))
            self.nation.setText(Ui_Player._NATIONALITIES[player['nationality']])
            
            self.attprow.setText(str(player['attprow']))
            self.defprow.setText(str(player['defprow']))
            self.goalkeeping.setText(str(player['goalkeeping']))
            self.dribble.setText(str(player['dribbling']))
            self.finish.setText(str(player['finishing']))
            self.lowpass.setText(str(player['lowpass']))
            self.loftedpass.setText(str(player['loftedpass']))
            self.header.setText(str(player['header']))
            self.swerve.setText(str(player['swerve']))
            self.catching.setText(str(player['catching']))
            self.clearing.setText(str(player['clearing']))
            self.reflexes.setText(str(player['reflexes']))
            self.strball.setText(str(player['strball']))
            self.physcont.setText(str(player['physical']))
            self.kickpower.setText(str(player['kickingpower']))
            self.explopower.setText(str(player['explosivepower']))
            self.ballcontrol.setText(str(player['ballcontrol']))
            self.ballwinning.setText(str(player['ballwinning']))
            self.jump.setText(str(player['jump']))
            self.placekicking.setText(str(player['placekicking']))
            self.coverage.setText(str(player['coverage']))
            self.stamina.setText(str(player['stamina']))
            self.speed.setText(str(player['speed']))
            self.ide.setText("ID: " + str(player['pid']))
            self.facee.setText("Face: " + str(player['facee']))
            self.edite.setText("Edit: " + str(player['editedplayer']))
            self.agee.setText("Age: " + str(player['age']))
            self.bodye.setText("Body: " + str(player['height']) + "/" + str(player['weight']))
            if(player['strfoot'] == 0):
                self.foote.setText("Foot: " + 'Right')
            else:
                self.foote.setText("Foot: " + 'Left')
            self.pose.setText("Pos: " + self._POSLIST[player['regpos']])
            
            #Set colours
            for field in Ui_Editor._PDATAFIELDS:
                val = int(field.text())
                if(val >= 70):
                    if(val < 80):
                        field.setPalette(self.bronze)
                    elif(val >= 80 and val < 90):
                        field.setPalette(self.silver)
                    elif(val >= 90 and val < 99):
                        field.setPalette(self.gold)
                    elif(val == 99):
                        field.setPalette(self.full)
                else:
                    field.setPalette(self.nonmed)

    def editp(self, player):
        p = Player(self, player)
        p.pid.setText(str(player['pid']))
        p.pname.setText(player['name'])
        p.pshirtname.setText(player['print'])
        p.pcommid.setText(str(player['commid']))
        p.pnationality.setCurrentIndex(Ui_Player._NATINDEX[player['nationality']])
        p.pplayingstyle.setCurrentIndex(player['playstyle'])
        p.page.setText(str(player['age']))
        p.pheight.setText(str(player['height']))
        p.pweight.setText(str(player['weight']))
        p.pform.setCurrentIndex(player['form'])
        p.pfooting.setCurrentIndex(player['strfoot'])
        p.pwfacc.setCurrentIndex(player['wfacc'])
        p.pwfusage.setCurrentIndex(player['wfusage'])
        p.pinjuryres.setCurrentIndex(player['injuryres'])
        
        p.pregpos.setCurrentIndex(player['regpos'])
        for id, pos in player['playables'].items():
            if(int(pos) == 1):
                Ui_Player._PLAYABLES[id].setStyleSheet("background-color: #FFFF00")
            elif(int(pos) == 2):
                Ui_Player._PLAYABLES[id].setStyleSheet("background-color: #FF0000")
                
        p.pattprow.setText(str(player['attprow']))
        p.pdefprow.setText(str(player['defprow']))
        p.pgoalkeeping.setText(str(player['goalkeeping']))
        p.pdribbling.setText(str(player['dribbling']))
        p.pfinishing.setText(str(player['finishing']))
        p.plowpass.setText(str(player['lowpass']))
        p.ploftedpass.setText(str(player['loftedpass']))
        p.pheader.setText(str(player['header']))
        p.pswerve.setText(str(player['swerve']))
        p.pcatching.setText(str(player['catching']))
        p.pclearing.setText(str(player['clearing']))
        p.preflexes.setText(str(player['reflexes']))
        p.pstrball.setText(str(player['strball']))
        p.pphyscont.setText(str(player['physical']))
        p.pkickpower.setText(str(player['kickingpower']))
        p.pexplopower.setText(str(player['explosivepower']))
        p.pballcontrol.setText(str(player['ballcontrol']))
        p.pballwinning.setText(str(player['ballwinning']))
        p.pjump.setText(str(player['jump']))
        p.pcoverage.setText(str(player['coverage']))
        p.pplacekicking.setText(str(player['placekicking']))
        p.pstamina.setText(str(player['stamina']))
        p.pspeed.setText(str(player['speed']))
        
        for field in Ui_Player._STATS:
            stat = int(field.text())
            if(stat >= 70):
                if(stat < 80):
                    field.setPalette(self.bronze)
                elif(stat >= 80 and stat < 90):
                    field.setPalette(self.silver)
                elif(stat >= 90 and stat < 99):
                    field.setPalette(self.gold)
                elif(stat == 99):
                    field.setPalette(self.full)
            else:
                field.setPalette(self.nonmed)
        i = 0
        self.skillcount = 0
        for box in Ui_Player._SKILLS:
            if(i > 27):
                i = 0
            if(player['playerskills'][i]):
                box.setChecked(1)
                self.skillcount = self.skillcount + 1
            i = i + 1
        p.label_44.setText("Player Skills (" + str(self.skillcount) + "/10)")
        
        i = 0
        self.comcount = 0
        for box in Ui_Player._COMSTYLES:
            if(i > 6):
                i = 0
            if(player['comstyles'][i]):
                box.setChecked(1)
                self.comcount = self.comcount + 1
            i = i + 1
        p.label_46.setText("COM Styles (" + str(self.comcount) + "/5)")
        
        p.pdribhunch.setCurrentIndex(player['dhunchmotion'])
        p.pdribarm.setCurrentIndex(player['dribblearmmotion'])
        p.prunhunch.setCurrentIndex(player['rhunchmotion'])
        p.prunarm.setCurrentIndex(player['runarmmotion'])
        p.pckmot.setCurrentIndex(player['ckmotion'])
        p.pfkmot.setCurrentIndex(player['fkmotion'])
        p.ppkmot.setCurrentIndex(player['pkmotion'])
        
        p.pgoalcel1.setCurrentIndex(player['goal1'])
        p.pgoalcel2.setCurrentIndex(player['goal2'])
        
        p.pfacee.setChecked(player['facee'])
        p.phaire.setChecked(player['haire'])
        p.pphyse.setChecked(player['physe'])
        p.pstripe.setChecked(player['stripe']) 
        p.pskincol.setCurrentIndex(player['skincolour'])
        p.pgkgloves.setText(str(player['gkgloves']))
        p.pboots.setText(str(player['boots']))
        p.pwristtape.setCurrentIndex(player['wtape'])
        p.psleeves.setCurrentIndex(player['sleeves'])
        p.pshirttail.setCurrentIndex(player['shirttail'])
        p.psocks.setCurrentIndex(player['socks'])
        p.pankletape.setChecked(player['ankletape'])
        p.pglasses.setCurrentIndex(player['glasses'])
        p.pshorts.setCurrentIndex(player['unders'])
        
        p.pneckl.setValue(player['neckl']-7)
        p.pnecks.setValue(player['necks']-7)
        p.pshoulderh.setValue(player['shoulderh']-7)
        p.pshoulderw.setValue(player['shoulderw']-7)
        p.pchestm.setValue(player['chestm']-7)
        p.pwaists.setValue(player['waists']-7)
        p.parms.setValue(player['arms']-7)
        p.pthighs.setValue(player['thighs']-7)
        p.pcalfs.setValue(player['calfs']-7)
        p.plegl.setValue(player['legl']-7)
        p.parml.setValue(player['arml']-7)
        p.pheadw.setValue(player['headw']-7)
        p.pheadl.setValue(player['headl']-7)
        p.pheadd.setValue(player['headd']-7)
        
        p.show()
    
    def flags(self):
        if(self.loaded == 1):
            b = open('out/data.dat', 'r+b')
            for pid, data in self.players.items():
                data['facee'] = 0
                data['haire'] = 0
                data['physe'] = 0
                data['stripe'] = 0
                
                dat = data['facee']
                dat |= data['haire'] << 1
                dat |= data['physe'] << 2
                dat |= data['stripe'] << 3
                dat |= data['boots'] << 4
                dat |= data['gkgloves'] << 18
                dat |= data['appunknownb'] << 28
                
                b.seek(self._PLAYEROFFSET + data['findex']*188)
                b.seek(124, 1)
                b.write(pack('<I', dat))
            b.close()
            n = QMessageBox.information(self, 'Flags Reset', "All player flags reset successfully", QMessageBox.Ok)
    
    def tflags(self):
        if(self.loaded == 1):
            b = open('out/data.dat', 'r+b')
            b.seek(self._TEAMOFFSET)
            for pid, data in self.teams.items():
                b.seek(24, 1)
                b.write(pack('>I', 0x00100000))
                b.seek(452, 1)
            b.close()
            n = QMessageBox.information(self, 'Flags Reset', "All team flags reset successfully", QMessageBox.Ok)
    
    def bcopy(self):
        if(self.loaded == 1):
            b = open('out/data.dat', 'r+b')
            for pid, data in self.players.items():
                b.seek(self._PLAYEROFFSET + data['findex']*188)
                b.seek(124, 1)
                b.write(pack('<I', data['pid']))
            b.close()
            n = QMessageBox.information(self, 'Flags Reset', "All base copy IDs fixed successfully", QMessageBox.Ok)
    
    def setfpc(self):
        team = self.teamTable.currentItem().team
        b = open('out/data.dat', 'r+b')
        for pid in self.teams[team]['players']:
            self.players[pid]['boots'] = 38
            self.players[pid]['skincolour'] = 7
            self.players[pid]['glasses'] = 0
            self.players[pid]['unders'] = 0
            self.players[pid]['wtape'] = 0
            self.players[pid]['socks'] = 2
            self.players[pid]['shirttail'] = 0
            self.players[pid]['ankletape'] = 0
            self.players[pid]['sleeves'] = 2
            
            if(self.players[pid]['regpos'] == 0):
                self.players[pid]['sleeves'] = 1
                self.players[pid]['gkgloves'] = 12
                
            b.seek(self._PLAYEROFFSET + 188*self.players[pid]['findex'])
            b.seek(120, 1)
            
            dat = self.players[pid]['facee']
            dat |= self.players[pid]['haire'] << 1
            dat |= self.players[pid]['physe'] << 2
            dat |= self.players[pid]['stripe'] << 3
            dat |= self.players[pid]['boots'] << 4
            dat |= self.players[pid]['gkgloves'] << 18
            dat |= self.players[pid]['appunknownb'] << 28
            b.write(pack('<I', dat))
            
            b.seek(11, 1)
            
            dat = self.players[pid]['wtapeextra']
            dat |= self.players[pid]['wtape'] << 6
            b.write(pack('<B', dat))

            dat = self.players[pid]['glassescol']
            dat |= self.players[pid]['glasses'] << 3
            dat |= self.players[pid]['sleeves'] << 6
            dat |= self.players[pid]['inners'] << 8
            dat |= self.players[pid]['socks'] << 10
            dat |= self.players[pid]['unders'] << 12
            dat |= self.players[pid]['shirttail'] << 14
            dat |= self.players[pid]['ankletape'] << 15
            b.write(pack('<H', dat))
            
            b.seek(23, 1)
            dat = self.players[pid]['skincolour']
            dat |= self.players[pid]['appunknownf'] << 3
            b.write(pack('<B', dat))
            
        b.close()
        n = QMessageBox.information(self, 'FPC Applied', "FPC settings applied successfully", QMessageBox.Ok)
    
    def restfpc(self):
        team = self.teamTable.currentItem().team
        b = open('out/data.dat', 'r+b')
        for pid in self.teams[team]['players']:
            self.players[pid]['wtape'] = 2
    
            b.seek(self._PLAYEROFFSET + 188*self.players[pid]['findex'])
            b.seek(135, 1)
            
            dat = self.players[pid]['wtapeextra']
            dat |= self.players[pid]['wtape'] << 6
            b.write(pack('<B', dat))
        b.close()
        n = QMessageBox.information(self, 'Restore Applied', "Player restore settings applied successfully", QMessageBox.Ok)
    
    def save(self, type):
        if(type == 0):
            subprocess.call(['lib/encrypter18.exe', 'out', self.efile])
            n = QMessageBox.information(self, 'File Saved', "EDIT file saved successfully", QMessageBox.Ok)
        elif(type == 1):
            f = QFileDialog.getSaveFileName(self, 'Edit File', os.path.expanduser('~/Documents/KONAMI/Pro Evolution Soccer 2017/save/').replace("C:", "G:"), "")
            subprocess.call(['lib/encrypter18.exe', 'out', f[0]])
            n = QMessageBox.information(self, 'File Saved', "EDIT file saved successfully", QMessageBox.Ok)
    
    def closeEvent(self, event):
        if(self.saved == 1):
            n = QMessageBox.question(self, 'Close Application', "Unsaved changes will be lost. Are you sure you want to exit?", QMessageBox.Yes, QMessageBox.No)
            if(n == QMessageBox.Yes):
                event.accept()
            if(n == QMessageBox.No):
                event.ignore()
                
    def closef(self):
        if(self.saved == 1):
            n = QMessageBox.question(self, 'Close Application', "Unsaved changes will be lost. Are you sure you want to exit?", QMessageBox.Yes, QMessageBox.No)
            if(n == QMessageBox.Yes):
                sys.exit(0)
        else:
            sys.exit(0)
                        
if __name__ == "__main__":
    p = QApplication(sys.argv)
    w = Editor()
    w.show()
    sys.exit(p.exec_())