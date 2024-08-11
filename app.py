import os
import ast
from flask import Flask, request, render_template, redirect, url_for
from flask import session as flask_session #advaith
from flask_session import Session
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

app = Flask(__name__)


UPLOAD_FOLDER = 'static/inf'
UPLOAD_FOLDER_SPN= 'static\\spn'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER1'] = UPLOAD_FOLDER_SPN
#advaith
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
Session(app)

Base = declarative_base()
engine = create_engine('sqlite:///collabhub.db', echo=True)
SessionLocal = sessionmaker(bind=engine)

class Influencer(Base):
    __tablename__ = 'Influencers'
    Username = Column(String, unique=True, primary_key=True)  # Use Username as the primary key
    Password = Column(String)
    Name = Column(String)
    EmailID = Column(String, unique=True)
    MobileNo = Column(Integer, unique=True)
    PhotoPath = Column(String)
    Reach = Column(Integer)
    AcceptedAds = Column(String, nullable=True)
    AdsInbox = Column(String, nullable=True)
    AdsNegotiation = Column(String, nullable=True)
    Earnings = Column(Numeric)
    Platforms = Column(String)
    Rating = Column(Numeric)

    # Define relationship to Advertisement
    advertisements = relationship("Advertisement", back_populates="influencer")


class Sponsor(Base):
    __tablename__ = 'Sponsors'
    SponsorID = Column(String, unique=True, primary_key=True)  # Use SponsorID as the primary key
    SponsorName = Column(String)
    Email = Column(String, unique=True)
    PhoneNumber = Column(Integer, unique=True)
    CampaignsList = Column(String, nullable=True)
    CampaignsNegotiation = Column(String, nullable=True)
    CampaignsNotAccepted = Column(String, nullable=True)
    Password = Column(String)
    CampaignIdList = Column(String, nullable=True)
    PhotoPath = Column(String)

    # Define relationship to Advertisement
    advertisements = relationship("Advertisement", back_populates="sponsor")


class Campaign(Base):
    __tablename__ = 'Campaign'
    CampaignID = Column(Integer, primary_key=True, autoincrement=True, unique=True)  # Integer with autoincrement
    CampaignName = Column(String)
    Category = Column(String)
    AdvertisementLists = Column(String)

    # Define relationship to Advertisement
    advertisements = relationship("Advertisement", back_populates="campaign")

class Advertisement(Base):
    __tablename__ = 'Advertisements'

    AdID = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    CampaignID = Column(String, ForeignKey('Campaign.CampaignID'))
    SpnUsername = Column(String, ForeignKey('Sponsors.SponsorID'))
    Status = Column(String)
    InfID = Column(String, ForeignKey('Influencers.Username'))
    Payment = Column(Numeric)
    Tasks = Column(String)
    AdName = Column(String)
    TotalTaskCount = Column(Integer)
    TasksCompleted = Column(Integer)

    # Relationships
    campaign = relationship("Campaign", back_populates="advertisements")
    influencer = relationship("Influencer", back_populates="advertisements")
    sponsor = relationship("Sponsor", back_populates="advertisements")

Base.metadata.create_all(bind=engine)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Login for Influencers
@app.route('/loginINF')
def index1():
    return render_template('login.html')
# POST to /loginINF
@app.route('/loginINF', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        dbsession = SessionLocal() #Advaith
        influencer = dbsession.query(Influencer).filter_by(Username=username, Password=password).first()
        dbsession.close()

        if influencer:
            flask_session['influencer_username'] = username # (Advaith) adding current username to session
            # Pass the retrieved attributes to the dashboard page
            return redirect("/dashboardINF")
        else:
            return "Invalid username or password. Please try again."
    return render_template('login.html')



# Registering Influencers
@app.route('/registerINF')
def registerINF_UI():
    return render_template('registerINF.html')
# POST method to /registerINF
@app.route('/registerINF', methods=['POST'])
def registerINF():
    username = request.form['username']
    password = request.form['password']
    cfpassword=request.form['cnfPassword']
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    reach = request.form['reach']
    earnings = 0
    photo = request.files['image']
    twttr= {'twitter':request.form.get('twitter')}
    yt = {'youtube':request.form.get('youtube')}
    inst = {'instagram':request.form.get('instagram')}
    fb = {'facebook':request.form.get('facebook')}
    tk = {'tiktok':request.form.get('tiktok')}
    tw = {'twitch':request.form.get('twitch')}
    print(type(request.form.get('twitch')))
    l=[twttr,yt,inst,fb,tk,tw]
    dict1={}
    for x in l:
        if (list(x.values())[0])!="":
            dict1[list(x.keys())[0]]=list(x.values())[0]

    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        photo_path = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        return "Invalid file format. Please upload a valid image."

    new_influencer = Influencer(
        Username=username,
        Password=password,
        Name=name,
        EmailID=email,
        MobileNo=mobile,
        PhotoPath=photo_path,
        Reach=reach,
        Earnings=earnings,
        Platforms=str(dict1),
        Rating=0
    )

    session = SessionLocal()
    try:
        session.add(new_influencer)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        return str(e)
    finally:
        session.close()
    # index1 is login page for influencers
    return redirect(url_for('index1'))



# Dashboard for Influencers (Advaith)
@app.route('/dashboardINF')
def dashboard():
    current_user = flask_session.get('influencer_username')
    session = SessionLocal()

    # Get influencer details
    influencer = session.query(Influencer).filter_by(Username=current_user).first()

    # Get accepted ads details
    accepted_ads = []
    if influencer.AcceptedAds:
        accepted_ads_ids = influencer.AcceptedAds.split(',')
        accepted_ads = session.query(Advertisement).filter(Advertisement.AdID.in_(accepted_ads_ids)).all()
        
    # Get ads requests
    ads_requests = []
    if influencer.AdsInbox:
        ads_requests_ids = influencer.AdsInbox.split(',')
        ads_requests = session.query(Advertisement).filter(Advertisement.AdID.in_(ads_requests_ids)).all()

    session.close()

    return render_template('infDashboard.html',
                           influencer=influencer,
                           accepted_ads=accepted_ads,
                           ads_requests=ads_requests)



def render_sponsor_dashboard(photo_path, sponsor_name, sponsor_id, ad_tasks):
    return render_template('spnDashboard.html',
                           PhotoPath=photo_path,
                           SponsorName=sponsor_name,
                           SponsorID=sponsor_id,
                           AdTasks=ad_tasks)
#inf search feature (Advaith)
@app.route('/searchINF', methods=['GET', 'POST'])
def searchINF():
    session = SessionLocal()
    try:
        campaigns = None 
        search_query = ''
        selected_industry = ''

        if request.method == 'POST':
            search_query = request.form['search_query']
            industry = request.form['industry']
            selected_industry = industry
            query = session.query(Campaign).filter(Campaign.CampaignName.like('%' + search_query + '%'))

            if industry:
                query = query.filter(Campaign.Category == industry)

            campaigns = query.all()

        industries = [industry[0] for industry in session.query(Campaign.Category).distinct().all()]
        return render_template('infSearch.html', campaigns=campaigns, industries=industries, search_query=search_query, selected_industry=selected_industry)
    finally:
        session.close()

#campaign details feature (Advaith)
@app.route('/campaign_details/<int:camp_id>', methods=['GET', 'POST'])
def campaign_details(camp_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    campaign = session.query(Campaign).filter_by(CampaignID=camp_id).first()
    if campaign:
        ads = session.query(Advertisement).filter_by(CampaignID=camp_id).all()
        influencer_username = flask_session.get('influencer_username')
        influencer_ads = session.query(Advertisement).filter_by(InfID=influencer_username).all()
        assigned_ads = [ad.AdID for ad in influencer_ads]

        for ad in ads:
            ad.parsed_tasks = eval(ad.Tasks)
        
        return render_template('campaign_details.html', campaign=campaign, ads=ads, assigned_ads=assigned_ads)
    else:
        return 'Campaign not found', 404


# Sponsor Login
@app.route('/loiginSPN')
def index2():
    return render_template('loginSPN.html')
# POST method to /loginSPN
@app.route('/loginSPN', methods=['GET', 'POST'])
def loginSPN():
    if request.method == 'POST':
        sponsor_id = request.form['username']
        password = request.form['password']

        session = SessionLocal()
        sponsor = session.query(Sponsor).filter_by(SponsorID=sponsor_id, Password=password).first()
        session.close()

        if sponsor:
            return render_sponsor_dashboard(sponsor.PhotoPath, sponsor.SponsorName, sponsor.SponsorID)
        else:
            return "Invalid Sponsor ID or password. Please try again."
    return render_template('loginSPN.html')




# Regsiter page for sponsors
@app.route('/registerSPN')
def registerSPN_UI():
    return render_template('registerSPN.html')
# POST method to /registerSPN
@app.route('/registerSPN', methods=['POST'])
def registerSPN():
    username = request.form['username']
    password = request.form['password']
    cfpassword=request.form['cnfPassword']
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    photo = request.files['image']

    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER1'], filename))
        photo_path = (os.path.join(app.config['UPLOAD_FOLDER1'], filename))
    else:
        return "Invalid file format. Please upload a valid image."

    new_sponsor = Sponsor(
        SponsorID=username,
        Password=password,
        SponsorName=name,
        Email=email,
        PhoneNumber=mobile,
        PhotoPath=photo_path,
        CampaignsList='',
        CampaignsNegotiation='',
        CampaignsNotAccepted='',
        CampaignIdList=''
    )

    session = SessionLocal()
    try:
        session.add(new_sponsor)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        return str(e)
    finally:
        session.close()
    # index2 is login page for sponsors
    return redirect(url_for('index2'))



@app.route('/add_campaign/<username>', methods=['GET', 'POST'])
def add_campaign(username):
    if request.method == 'POST':
        campaign_name = request.form['campaign_name']
        num_ads = int(request.form['num_ads'])
        industry=request.form['industry']
        return redirect(url_for('add_ads', username=username,campaign_name=campaign_name, num_ads=num_ads,industry=industry))
    return render_template('add_campaign.html')

@app.route('/add_ads/<username>/<campaign_name>/<industry>/<int:num_ads>', methods=['GET', 'POST'])
def add_ads(username, campaign_name, num_ads, industry):
    if request.method == 'POST':
        session = SessionLocal()
        try:
            new_campaign = Campaign(
                CampaignName=campaign_name,
                Category=industry,
                AdvertisementLists=''
            )
            session.add(new_campaign)
            session.commit()
            campaign_id = new_campaign.CampaignID
            ad_ids = []
            for i in range(num_ads):
                ad_name = request.form[f'ad_name_{i}']
                num_tasks = int(request.form[f'num_tasks_{i}'])
                task_details_str = request.form[f'task_details_{i}']
                earning = float(request.form[f'earning_{i}'])

                task_details_list = task_details_str.split('|')
                tasks = []
                for idx, task_detail in enumerate(task_details_list, start=1):
                    task_dict = {
                        'SlNo': idx,
                        'TaskDetail': task_detail.strip(),
                        'Status': 'PENDING'
                    }
                    tasks.append(task_dict)

                tasks_str = str(tasks)

                new_ad = Advertisement(
                    CampaignID=campaign_id,
                    SpnUsername=username,
                    Status='PENDING',
                    Tasks=tasks_str,
                    TotalTaskCount=num_tasks,
                    TasksCompleted=0,
                    Payment=earning,
                )
                session.add(new_ad)
                session.commit()

                ad_ids.append(new_ad.AdID)


            new_campaign.AdvertisementLists = ','.join(map(str, ad_ids))
            session.commit()

        except Exception as e:
            session.rollback()
            return "EXCEPTION>>>"+str(e)
        finally:
            sponsor = session.query(Sponsor).filter_by(SponsorID=username).first()
            session.close()
            ad_tasks=[]
            advertisements = session.query(Advertisement).filter_by(CampaignID=campaign_id).all()
            for ad in advertisements:
                tasks_list = eval(ad.Tasks)
                ad_tasks.extend(tasks_list)

            photo_path = sponsor.PhotoPath.replace("\\", "/")
            sponsor_name = sponsor.SponsorName
            sponsor_id = sponsor.SponsorID


        return render_sponsor_dashboard(photo_path, sponsor_name, sponsor_id, ad_tasks)
    return render_template('add_ads.html', campaign_name=campaign_name, num_ads=num_ads)


if __name__ == '__main__':
    app.run(debug=True)
