from zope.interface import Interface
from zope.schema import TextLine
from zope.schema import Date
from zope.schema import Choice
from zope.schema import Bool
from zope.schema import Float
from zope.schema import Int
from zope.i18nmessageid import MessageFactory
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile

_ = MessageFactory('stroke_form')

from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import form, field
from z3c.form.browser.radio import RadioFieldWidget

from zope.interface import Invalid
from z3c.form.interfaces import ActionExecutionError

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


from plone.autoform import directives
import plone.app.z3cform
import plone.z3cform.templates

YesNoVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'Y', title=_(u'Yes')),
     SimpleTerm(value=u'N', title=_(u'No')),]
    )
    
YesNoUnknownVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'Y', title=_(u'Yes')),
     SimpleTerm(value=u'N', title=_(u'No')),
     SimpleTerm(value=u'U', title=_(u'Unknown')),]
    )
    
EventVocabulary = SimpleVocabulary(
     [SimpleTerm(value=u'SM', title=_(u'Major non-disabling stroke')),
     SimpleTerm(value=u'S', title=_(u'Minor stroke')),
     SimpleTerm(value=u'TM', title=_(u'Multiple cerebral TIAs')),
     SimpleTerm(value=u'T', title=_(u'Single cerebral TIA')),
     SimpleTerm(value=u'OC', title=_(u'Monocular')),]
     )
     
GenderVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'M', title=_(u'Male')),
     SimpleTerm(value=u'F', title=_(u'Female')),]
    )



class IStrokeForm(Interface):


    age = Int(
        title=_(u"Age in years (between 40 and 100)"),
        required=True,
        min=40,
        max=100,
            )
            
    directives.widget('sex',RadioFieldWidget)
    sex = Choice(
         title=u'Sex',
         vocabulary=GenderVocabulary,
         required=True,
         )
         
    directives.widget('noccl',RadioFieldWidget)
    noccl = Choice(
        title=u'Near occlusion',
        vocabulary=YesNoUnknownVocabulary,
        )
        
    car = Float(
        title=_(u"Carotid stenosis on symptomatic side (percentage, between 50 and 99)"),
        min=50.0,
        max=99.0,
        required=False
            )
            
    tslev = Int(
        title=_(u"Time in days since last event (between 7 and 180 days)"),
        min=7,
        max=180,
            )
            
    directives.widget('event',RadioFieldWidget)
    event = Choice(
        title=u'Primary symptomatic event',
        vocabulary=EventVocabulary
        )
        
    directives.widget('diab',RadioFieldWidget)
    diab = Choice(
        title=u'Diabetes',
        vocabulary=YesNoVocabulary,
        default="N",
        required=True,
    )
    
    directives.widget('mi',RadioFieldWidget)
    mi = Choice(
        title=u'Myocardial Infarction',
        default="N",
        vocabulary=YesNoVocabulary,
        required=True,
    )
    
    directives.widget('pvd',RadioFieldWidget)
    pvd = Choice(
        title=u'Peripheral vascular disease',
        vocabulary=YesNoVocabulary,
        default="N",
        required=True,
    )
    
    directives.widget('hypert',RadioFieldWidget)
    hypert = Choice(
        title=u'Treated hypertension',
        vocabulary=YesNoVocabulary,
        default="N",
        required=True,
    )
        
    directives.widget('pla',RadioFieldWidget)
    pla= Choice(
        title=u'Irregular/ulcerated plaque surface',
        vocabulary=YesNoUnknownVocabulary,
        default="N",
        required=True,
        )
        
    
            
class StrokeForm(form.Form):

    fields = field.Fields(IStrokeForm)

    ignoreContext = True

    output = None
   
    # def __init__(self, context, request):
    #
    #     self.request.response.setHeader('X-Frame-Options', 'ALLOWALL')

    def updateWidgets(self):
        super(StrokeForm, self).updateWidgets()

    @button.buttonAndHandler(u'Submit')
    def handleSave(self, action):
        data, errors = self.extractData()
        
        if 'car' in data.keys():

            if (data['car'] in range(1,99)) and (data['noccl'] == 'Y'):
                raise ActionExecutionError(Invalid(u'Please check the stenosis value! It should be either a numeric value or near occlusion but not both.'))
            

        if errors:
            self.status = self.formErrorsMessage
            return

        self.output = self.calcRisk(data)
        self.status = _(u"Calculation complete")


    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            "The form has been cleared",
            'info')
        redirect_url = "%s/@@strokeform" % self.context.absolute_url()
        self.request.response.redirect(redirect_url)
    
    def oneyearrange(self,riskinteger):
        
        if riskinteger < 5:
            text = "less than 5"
        elif riskinteger > 20:
            text = "exceeds 20"
        else:
            text = str(riskinteger)
        
        return text
        
    def fiveyearrange(self,riskinteger):
        
        if riskinteger < 10:
            text = "less than 10"
        elif riskinteger > 50:
            text = "exceeds 50"
        else:
            text = str(riskinteger)
        
        return text
         
        
    def calcRisk(self,data):
        
        sex = data['sex']
        car = data['car']
        noccl = data['noccl']
        age = data['age']
        tslev = data['tslev']
        event = data['event']
        diab = data['diab']
        mi = data['mi']
        pvd = data['pvd']
        hypert = data['hypert']
        pla = data['pla']
        
        formvalues = {}
        riskval = 0
        
        if sex =='M':
            riskval = riskval + (1 - 0.71854305) * 0.17618
            formvalues['sex'] ='male'
        elif sex =='F':
            riskval = riskval + (0 - 0.71854305) * 0.17618
            formvalues['sex'] ='female'
        else:
            formvalues['sex'] = ""

        if car > 0:
             riskval = riskval + (car/10 - 3.62661424) * 0.16201
             formvalues['car']= str(car)
        else:
             formvalues['car']= 0


        if noccl =='Y':
            riskval = riskval + (1 - 0.03062914)* (-0.71454)
        # if near occlusion we use stenosis value of 84.5 - midvalue between 70 and 99
            riskval = riskval + (84.5/10 - 3.62661424) * 0.16201
            formvalues['noccl']="Yes"
        elif noccl =='N':
            riskval = riskval + (0 - 0.03062914)* (-0.71454)
            formvalues['noccl']="No"
        elif noccl =='U':
            formvalues['noccl']='Unknown'
        else:
            formvalues['noccl']=""

        if age > 0:
            riskval = riskval + (age/10 - 6.23071192) * 0.10874
            formvalues['age']=str(age)
        else:
            formvalues['age']=''
           

        if tslev > -1:
            riskval = riskval + (tslev/7 - 8.881386) * (-0.04214)
            formvalues['tslev']=str(tslev)
        else:
            formvalues['tslev']=''

        if event =='OC' :
            formvalues['event'] = "Monocular"
            riskval = riskval + (0 - 0.19784768) * 0.34097
            riskval = riskval + (0 - 0.16970199) * 0.71518
            riskval = riskval + (0 - 0.1763245) * 0.59875
            riskval = riskval + (0 - 0.25082781) * 0.93125
        elif event =='T' :
            formvalues['event'] = "Single cerebral TIA"
            riskval = riskval + (1 - 0.19784768) * 0.34097
            riskval = riskval + (0 - 0.16970199) * 0.71518
            riskval = riskval + (0 - 0.1763245) * 0.59875
            riskval = riskval + (0 - 0.25082781) * 0.93125
        elif event =='TM' :
            formvalues['event'] = "Multible cerebral TIAs";
            riskval = riskval + (0 - 0.19784768) * 0.34097
            riskval = riskval + (1 - 0.16970199) * 0.71518
            riskval = riskval + (0 - 0.1763245) * 0.59875
            riskval = riskval + (0 - 0.25082781) * 0.93125
        elif event =='S' :
            formvalues['event'] = "Minor stroke";
            riskval = riskval + (0 - 0.19784768) * 0.34097;
            riskval = riskval + (0 - 0.16970199) * 0.71518;
            riskval = riskval + (1 - 0.1763245) * 0.59875;
            riskval = riskval + (0 - 0.25082781) * 0.93125;
        elif event =='SM' :
            formvalues['event'] = "Major non-disabling stroke";
            riskval = riskval + (0 - 0.19784768) * 0.34097
            riskval = riskval + (0 - 0.16970199) * 0.71518
            riskval = riskval + (0 - 0.1763245) * 0.59875
            riskval = riskval + (1 - 0.25082781) * 0.93125
        else:
            formvalues['event']= ""

        if diab =='Y' :
            riskval = riskval + (1 - 0.12003311) * 0.30055
            formvalues['diab']='Yes'
        elif diab =='N' :
            riskval = riskval + (0 - 0.12003311) * 0.30055
            formvalues['diab']='No'
        else:
            formvalues['diab']=""

        if mi =='Y':
            riskval = riskval + (1 - 0.11258278) * 0.45166
            formvalues['mi']="Yes"
        elif mi =='N' :
            riskval = riskval + (0 - 0.11258278) * 0.45166
            formvalues['mi']="No"     
        else:
            formvalues['mi']=""

        if pvd =='Y' :
            riskval = riskval + (1 - 0.17384106) * 0.16255
            formvalues['pvd']='Yes'            
        elif pvd =='N' :
            riskval = riskval + (0 - 0.17384106) * 0.16255
            formvalues['pvd']='No'
        else:
            formvalues['pvd']=''

        if hypert =='Y' :
           riskval = riskval + (1 - 0.37168874) * 0.2167
           formvalues['hypert'] = "Yes"
        elif hypert =='N' :
            riskval = riskval + (0 - 0.37168874) * 0.2167
            formvalues['hypert']= "No"
        else:
            formvalues['hypert']=""
        

        if pla =='Y' :
            riskval = riskval + (1 - 0.67384106) * 0.70738
            formvalues['pla']="Yes"
        elif pla =='N' :
            riskval = riskval + (0 - 0.67384106) * 0.70738
            formvalues['pla']="No"
        elif pla == 'U':
            formvalues['pla']="Unknown"
        else:
            formvalues['pla']=""
    
        totalscore = int(riskval*100)/100
        exptotal = 2.71828182845905 ** riskval
        surviv5 = 0.90042 ** exptotal 
        surviv1 = 0.96258 ** exptotal    
        risk5 = (1 - surviv5) * 100
        risk1 = (1 - surviv1) * 100

        exptot_int = int(exptotal*100)/100
        risk5_int = int(risk5*10)/10
        risk1_int = int(risk1*10)/10

        # if (risk5_int < 10):
        #     risk5_int_txt = "less than 10"
        #
        # if (risk5_int > 50):
        #     risk5_int_txt = "exceeds 50"
        #
        # if (risk1_int < 5):
        #     risk1_int_txt = "less than 5"
        #
        # if (risk1_int > 20):
        #     risk1_int_txt = "exceeds 20"
            
        txtoption = 1
        values = {'risk1_int': self.oneyearrange(risk1_int), 
                  'risk5_int': self.fiveyearrange(risk5_int),
                 }
            
            
        if noccl == 'U' and pla != 'U': 
            val_noccl_n = riskval + (0 - 0.03062914)* (-0.71454)
            val_noccl_y = riskval + (1 - 0.03062914)* (-0.71454)
            # if near occlusion we use stenosis value of 84.5 - midvalue between 70 and 99
            # therefore we substitute previous calculation based on the value of stenosis with this one
            val_noccl_y = val_noccl_y - (float(formvalues['car'])/10 - 3.62661424) * 0.16201
            val_noccl_y = val_noccl_y + (84.5/10 - 3.62661424) * 0.16201

            totalscore_n = int(val_noccl_n*100)/100
            exptotal_n = 2.71828182845905 ** val_noccl_n
            surviv5_n = 0.90042 ** exptotal_n 
            surviv1_n = 0.96258 ** exptotal_n 
            risk5_n = (1 - surviv5_n) * 100
            risk1_n = (1 - surviv1_n) * 100
            risk5_int_n = int(risk5_n*10)/10
            risk1_int_n = int(risk1_n*10)/10
            # if (risk5_int_n < 10):
            #     risk5_int_n = "less than 10"
            #
            # if (risk5_int_n > 50):
            #     risk5_int_n_txt = "exceeds 50"
            #
            # if (risk1_int_n < 5):
            #     risk1_int_n_txt = "less than 5"
            #
            # if (risk1_int_n > 20):
            #     risk1_int_n_txt = "exceeds 20"
            #

            totalscore_y = int(val_noccl_y*100)/100
            exptotal_y = 2.71828182845905 ** val_noccl_y
            surviv5_y = 0.90042 ** exptotal_y 
            surviv1_y = 0.96258 ** exptotal_y 
            risk5_y = (1 - surviv5_y) * 100
            risk1_y = (1 - surviv1_y) * 100
            risk5_int_y = int(risk5_y*10)/10
            risk1_int_y = int(risk1_y*10)/10
            # if (risk5_int_y < 10):
            #     risk5_int_y = "less than 10"
            #
            # if (risk5_int_y > 50):
            #     risk5_int_y = "exceeds 50"
            #
            # if (risk1_int_y < 5):
            #     risk1_int_y = "less than 5"
            #
            # if (risk1_int_y > 20):
            #     risk1_int_y = "exceeds 20"
            #     
            
            txtoption = 2
            values={'risk1_int_n':self.oneyearrange(risk1_int_n), 
                   'risk5_int_n':self.fiveyearrange(risk5_int_n),
                   'risk1_int_y':self.oneyearrange(risk1_int_y), 
                   'risk5_int_y':self.fiveyearrange(risk5_int_y),
                   }

            
        if (noccl != 'U' and pla == 'U') :
            val_pla_n = riskval + (0 - 0.67384106) * 0.70738
            val_pla_y = riskval + (1 - 0.67384106) * 0.70738

            totalscore_n = int(val_pla_n*100)/100
            exptotal_n = 2.71828182845905 ** val_pla_n
            surviv5_n = 0.90042 ** exptotal_n 
            surviv1_n = 0.96258 ** exptotal_n 
            risk5_n = (1 - surviv5_n) * 100
            risk1_n = (1 - surviv1_n) * 100
            risk5_int_n = int(risk5_n*10)/10
            risk1_int_n = int(risk1_n*10)/10
            
            # if (risk5_int_n < 10) :
            #     risk5_int_n_txt = "less than 10"
            #
            # if (risk5_int_n > 50) :
            #     risk5_int_n_txt = "exceeds 50"
            #
            # if (risk1_int_n < 5) :
            #     risk1_int_n_txt = "less than 5"
            #
            # if (risk1_int_n > 20) :
            #     risk1_int_n_txt = "exceeds 20"
        

            totalscore_y = int(val_pla_y*100)/100
            exptotal_y = 2.71828182845905 ** val_pla_y
            surviv5_y = 0.90042 ** exptotal_y 
            surviv1_y = 0.96258 ** exptotal_y 
            risk5_y = (1 - surviv5_y) * 100
            risk1_y = (1 - surviv1_y) * 100
            risk5_int_y = int(risk5_y*10)/10
            risk1_int_y = int(risk1_y*10)/10
            
            # if (risk5_int_y < 10) :
            #     risk5_int_y_txt = "less than 10"
            #
            # if (risk5_int_y > 50) :
            #     risk5_int_y_txt = "exceeds 50"
            #
            # if (risk1_int_y < 5) :
            #     risk1_int_y_txt = "less than 5"
            #
            # if (risk1_int_y > 20) :
            #     risk1_int_y_txt = "exceeds 20"
            
            txtoption = 3
            values={'risk1_int_n':self.oneyearrange(risk1_int_n), 
                   'risk5_int_n':self.fiveyearrange(risk5_int_n),
                   'risk1_int_y':self.oneyearrange(risk1_int_y), 
                   'risk5_int_y':self.fiveyearrange(risk5_int_y),
                   }
        
        if (noccl == 'U' and pla == 'U') :
            val_noccl_n = riskval + (0 - 0.03062914)* (-0.71454)
            val_noccl_y = riskval + (1 - 0.03062914)* (-0.71454)
            # if near occlusion we use stenosis value of 84.5 - midvalue between 70 and 99
            # therefore we substitute previous calculation based on the value of stenosis with this one
            val_noccl_y = val_noccl_y - (float(formvalues['car']) - 3.62661424) * 0.16201
            val_noccl_y = val_noccl_y + (84.5/10 - 3.62661424) * 0.16201

            # both near occlusion and irregular/ulcerated plaque 
            val_both = val_noccl_y + (1 - 0.67384106) * 0.70738
            # near occlusion and regular plaque
            val_nocc = val_noccl_y + (0 - 0.67384106) * 0.70738
            # -- no near occlusion and irregular/ulcerated plaque 
            val_plaq = val_noccl_n + (1 - 0.67384106) * 0.70738
            # -- neither near occlusion nor irregular/ulcerated plaque 
            val_none = val_noccl_n + (0 - 0.67384106) * 0.70738

            total_both = int(val_both*100)/100
            exptot_both = 2.71828182845905 ** val_both
            surviv5_both = 0.90042 ** exptot_both 
            surviv1_both = 0.96258 ** exptot_both 
            risk5_both = (1 - surviv5_both) * 100
            risk1_both = (1 - surviv1_both) * 100
            risk5_int_both = int(risk5_both*10)/10
            risk1_int_both = int(risk1_both*10)/10
            
            # if (risk5_int_both < 10) :
            #     risk5_int_both_txt = "less than 10"
            #
            # if (risk5_int_both > 50) :
            #     risk5_int_both_txt = "exceeds 50"
            #
            # if (risk1_int_both < 5) :
            #     risk1_int_both_txt = "less than 5"
            #
            # if (risk1_int_both > 20) :
            #     risk1_int_both_txt = "exceeds 20"
            

            total_nocc = int(val_nocc*100)/100
            exptot_nocc = 2.71828182845905 ** val_nocc
            surviv5_nocc = 0.90042 ** exptot_nocc 
            surviv1_nocc = 0.96258 ** exptot_nocc 
            risk5_nocc = (1 - surviv5_nocc) * 100
            risk1_nocc = (1 - surviv1_nocc) * 100
            risk5_int_nocc = int(risk5_nocc*10)/10
            risk1_int_nocc = int(risk1_nocc*10)/10
            
            # if (risk5_int_nocc < 10) :
            #     risk5_int_nocc_txt = "less than 10"
            #
            # if (risk5_int_nocc > 50) :
            #     risk5_int_nocc_txt = "exceeds 50"
            #
            # if (risk1_int_nocc < 5) :
            #     risk1_int_nocc_txt = "less than 5"
            #
            # if (risk1_int_nocc > 20) :
            #     risk1_int_nocc_txt = "exceeds 20"
            

            total_plaq = int(val_plaq*100)/100
            exptot_plaq = 2.71828182845905 ** val_plaq
            surviv5_plaq = 0.90042 ** exptot_plaq 
            surviv1_plaq = 0.96258 ** exptot_plaq 
            risk5_plaq = (1 - surviv5_plaq) * 100
            risk1_plaq = (1 - surviv1_plaq) * 100
            risk5_int_plaq = int(risk5_plaq*10)/10
            risk1_int_plaq = int(risk1_plaq*10)/10
            
            # if (risk5_int_plaq < 10) :
            #     risk5_int_plaq_txt = "less than 10"
            #
            # if (risk5_int_plaq > 50) :
            #     risk5_int_plaq_txt = "exceeds 50"
            #
            # if (risk1_int_plaq < 5) :
            #     risk1_int_plaq_txt = "less than 5"
            #
            # if (risk1_int_plaq > 20) :
            #     risk1_int_plaq_txt = "exceeds 20"
            #

            total_none = int(val_none*100)/100
            exptot_none = 2.71828182845905 ** val_none
            surviv5_none = 0.90042 ** exptot_none 
            surviv1_none = 0.96258 ** exptot_none 
            risk5_none = (1 - surviv5_none) * 100
            risk1_none = (1 - surviv1_none) * 100
            risk5_int_none = int(risk5_none*10)/10
            risk1_int_none = int(risk1_none*10)/10
            
            # if (risk5_int_none < 10) :
            #     risk5_int_none_txt = "less than 10"
            #
            # if (risk5_int_none > 50) :
            #     risk5_int_none_txt = "exceeds 50"
            #
            # if (risk1_int_none < 5) :
            #     risk1_int_none_txt = "less than 5"
            #
            # if (risk1_int_none > 20) :
            #     risk1_int_none_txt = "exceeds 20"
            
            txtoption = 4
            values={'risk1_int_both': self.oneyearrange(risk1_int_both), 
                   'risk5_int_both': self.fiveyearrange(risk5_int_both),
                   'risk1_int_nocc': self.oneyearrange(risk1_int_nocc), 
                   'risk5_int_nocc': self.fiveyearrange(risk5_int_nocc),
                   'risk1_int_plaq':self.oneyearrange(risk1_int_plaq), 
                   'risk5_int_plaq':self.fiveyearrange(risk5_int_plaq),
                   'risk1_int_none':self.oneyearrange(risk1_int_none), 
                   'risk5_int_none':self.fiveyearrange(risk5_int_none),
                   }
                   
        return formvalues, txtoption, values


StrokeFormView = plone.z3cform.layout.wrap_form(StrokeForm, index=FiveViewPageTemplateFile("stroke_form.pt"))
                
    
        
    
    
    
    
         