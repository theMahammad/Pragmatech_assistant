from flask import Flask,redirect,url_for,render_template,request
from flask.helpers import get_template_attribute
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,migrate

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
migrate = Migrate(app,db)
color_product=db.Table('color_product',
    db.Column('color_id', db.Integer, db.ForeignKey('color.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)
class Category(db.Model):

    id=db.Column(db.Integer,primary_key=True) 
    name=db.Column(db.String(100)) 
    products=db.relationship('Product', backref='category', lazy=True)
class Product(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer,nullable=False)
    category_id=db.Column(db.Integer,db.ForeignKey('category.id'),nullable=False)
    colors= db.relationship('Color', secondary=color_product, lazy='subquery',
        backref=db.backref('products', lazy=True))
class Color(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    

def getAll(class_):
    return class_.query.all()


def add_color(color): 
    existing_color = Color.query.filter(Color.name == color.lower()).one_or_none()
    if existing_color is not None:
        return existing_color
    else:
       new_color = Color()
       new_color.name = color.lower()
       return new_color
@app.route('/',methods=['GET','POST'])
def home():
    
    return render_template('index.html')
@app.route('/add_product',methods=['GET','POST'])
def addProduct():
    categories = getAll(Category)
    products=getAll(Product)
    if request.method=="POST":
        product_name = request.form['product_name']
       
        product_price = int(request.form['product_price'])
        product_category = int(request.form['product_category'])
        product_object = Product(name=product_name,price=product_price,category_id=product_category)

        color_product_string= request.form["product_colors"]
        colors_product=color_product_string.split(",")
        for color in colors_product:
           color_product_ = add_color(color)
           print(color_product_)
           product_object.colors.append(color_product_)
            
           
        selected_category=Category.query.get(product_category)
        selected_category.products.append(product_object)
        db.session.commit()
        return redirect("/add_product")
    return render_template('/add_product.html',categories=categories,products=products,Category=Category)
@app.route('/add_category',methods=['GET','POST'])
def addCategory():
    categories = getAll(Category)
    if request.method=="POST":
        category_name = request.form['category_name']
        category_object=Category(name=category_name)
        db.session.add(category_object)
        db.session.commit()
        return redirect("/add_category")
    return render_template("add_category.html",categories=categories)
if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)

