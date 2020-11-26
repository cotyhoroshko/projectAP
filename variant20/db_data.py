from database import Session, User, Advertisement, ModifierEnum

session = Session()

maks = User(name='Maksym Prihara', email='maxick99@lpnu.ua', password_hash='vfhajshjbdsdfsbdsbjdsfj')
vasyl = User(name='Vasl Zibrov', email='nolabs@lnu.ua', password_hash='dufhvfdskajdvk')

garage = Advertisement(modifier=ModifierEnum.local, summary='Selling garage', description='Selling a garage on Sykhiv', topic='transport', user=vasyl)
course_work = Advertisement(summary='Doing course works', description='Doing different course works on different '
                                                                      'subjects related to chemistry', topic='study',
                            modifier=ModifierEnum.public, user=maks)
poland = Advertisement(modifier=ModifierEnum.public, summary='Travelling to Poland', user=maks, description='A Volkswagen Transporter '
                                                                                          'deriving you to a '
                                                                                          'beautiful country',
                       topic='travelling')

session.add_all([maks, vasyl])
session.add_all([garage, course_work, poland])
session.commit()
