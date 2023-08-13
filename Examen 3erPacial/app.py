from flask import Flask, Response, render_template, request, redirect, send_file,url_for,flash #Importar libreria
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask import Flask, render_template, Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)

# Configura la conexión a la base de datos y otras configuraciones aquí


#Config
from config import config

#Database
from flask_mysqldb import MySQL

#Models
from models.modelUser import ModelUser

#Entities
from models.entities.user import User

app=Flask(__name__) #Inicializacion del servidor Flask

#Configuraciones para la conexion de   
app.config['MYSQL_HOST']="localhost" #Especificar en que servidor trabajamos
app.config['MYSQL_USER']="root" #Especificar usuario
app.config['MYSQL_PASSWORD']="" #Especificar contraseña
app.config['MYSQL_DB']="consultorio" #Especificar a que base de datos

app.secret_key='mysecretkey' #Permite hacer envios a traves de post

mysql=MySQL(app)
login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql, id)

#Declaracion de rutas

#Declarar ruta Index/principal http//localhost:5000
#Ruta se compone de nombre y funcion
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    rfc=request.form['rfc']
    contraseña=request.form['contraseña']
    if request.method=='POST':
        
        user = User(0, rfc, contraseña)
        logged_user = ModelUser.login(mysql, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('inicio'))
            else:
                flash ('Contraseña incorrecta')
                return render_template ('login.html')
        else:
            flash ('RFC no encontrado')
            return render_template ('login.html')
    else:
        return render_template ('login.html')


@app.route('/menu_admin')
def menu_admin():
        return render_template('menu_admin.html')

@app.route('/menu_usuario')
def menu_usuario():
        # Renderizar el panel de usuario
        return render_template('menu_usuario.html')

    
@app.route('/logout')
def logout():
    logout_user()
    return render_template ('index.html')

@app.route('/inicio')
@login_required
def inicio():
    return render_template('inicio.html')


@app.route('/guardarPaciente',methods=['GET','POST'])
def guardarPaciente():
    if request.method=='POST': #Peticiones del usuario a traves del metodo POST
        _medico=request.form['medico']
        _paciente=request.form['paciente']
        _ap=request.form['AP']
        _am=request.form['AM']
        _fn=request.form['FN']
        _ec=request.form['EC']
        _al=request.form['AL']
        _af=request.form['AF']
        #print(titulo,artista,anio)
        CS=mysql.connection.cursor()
        CS.execute('insert into expediente_paciente(medico,paciente,ap,am,fn,ec,al,af) values(%s,%s,%s,%s,%s,%s,%s,%s)',
                   (_medico,_paciente,_ap,_am,_fn,_ec,_al,_af)) #Para ejecutar codigo sql, y pasamos parametros
        mysql.connection.commit()

    flash('Paciente registrado exitosamente') #este mnsj se imprime en el CRUD de albums
    #return redirect(url_for('index')) #Reedireccionamiento a la vista index
    return render_template('expediente_paciente.html')

@app.route('/guardarMedico',methods=['GET','POST'])
def guardarMedico():
    if request.method=='POST': #Peticiones del usuario a traves del metodo POST
        _nombre=request.form['nombre']
        _ap=request.form['AP']
        _am=request.form['AM']
        _cp=request.form['CP']
        _pass=request.form['pass']
        _ce=request.form['CE']
        _rol=request.form['rol']
        #print(titulo,artista,anio)
        CS=mysql.connection.cursor()
        CS.execute('insert into registrar_usuario(nombre,ap,am,cedulap,contrasena,correo,rol) values(%s,%s,%s,%s,%s,%s,%s)',
                   (_nombre,_ap,_am,_cp,_pass,_ce,_rol)) #Para ejecutar codigo sql, y pasamos parametros
        mysql.connection.commit()

    flash('Médico registrado exitosamente')
    #return redirect(url_for('index')) #Reedireccionamiento a la vista index
    return render_template('registrar_medico.html')

@app.route('/exploracionPaciente',methods=['GET','POST'])
def exploracionPaciente():

    return render_template('exploracion_paciente.html')

@app.route('/diagnosticoPaciente',methods=['GET','POST'])
def diagnosticoPaciente():

    return render_template('diagnostico_paciente.html')

@app.route('/actualizarPaciente',methods=['GET','POST'])
def actualizarPaciente():

    return render_template('actualizar_paciente.html')

@app.route('/buscarMedico',methods=['GET','POST'])
def buscarMedico():
    Bnom=request.form.get('user_RFC')
    curBusq=mysql.connection.cursor()
    curBusq.execute('select * from medico where rfc LIKE %s', (f'%{Bnom}%',))
    busqueda=curBusq.fetchall()
    return render_template('buscar_medico.html', busqmed=busqueda)

#Consultar todas las citas que ha tenido el paciente, filtrada por el nombre del paciente y/o fecha de la cita
@app.route('/consultarCita',methods=['GET','POST'])
def consultarCita():
    Cnom=request.form.get('user_nombre')
    curSelect=mysql.connection.cursor()
    curSelect.execute('select id from persona where nombre=? ',(Cnom,))
    consulta=curSelect.fetchone()
    if consulta:
        curSelect.execute('select * from expediente_paciente where id_persona=?',(consulta[0],))
        Ccitas=curSelect.fetchall()
    return render_template('consultar_citas.html',tbcita=Ccitas)

@app.route('/consultarCita',methods=['GET','POST'])
def consultarCita():

    return render_template('consultar_citas.html')

@app.route('/consultarPaciente',methods=['GET','POST'])
def consultarPaciente():

    return render_template('consultar_paciente.html')

@app.route('/descargarReceta',methods=['GET','POST'])
def descargarReceta():

    return render_template('descargar_receta.html')

@app.route('/eliminarMedico',methods=['GET','POST'])
def eliminarMedico():

    return render_template('eliminar_medico.html')

# ERROR HTML PARA SOLICITUDES MAL FORMADAS (ERROR 400)
@app.errorhandler(400)
def status_400(error):
    return "<h1>Solicitud mal formada</h1>", 400

#ERROR HTML PARA USUARIOS QUE NO HAN INGRESADO (ERROR 401)
def status_401(error):
    return redirect(url_for('login'))


#ERROR HTML PARA URL NO ENCONTRADAS (ERROR 404)
def status_404(eror):
    return "<h1> Página no encontrada </h1>", 404

#Ejecucion del servidor
if __name__=='__main__':
    app.run()
    app.config.from_object(config['development'])
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(port=5005,debug=True) #Procurar que sea un puerto desocupado, debug(prendido)