from flask import Flask, render_template, request, redirect,url_for,flash,session,flash, Response #Importar libreria

#LOGIN
from flask_login import LoginManager, login_user, logout_user, login_required

#Config
from config import config

#Database
from flask_mysqldb import MySQL

#Models
from models.modelUser import ModelUser

#Entities
from models.entities.user import User

#Importaciones para PDF
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app=Flask(__name__) #Inicializacion del servidor Flask

#Configuraciones para la conexion de   
app.config['MYSQL_HOST']="localhost" #Especificar en que servidor trabajamos
app.config['MYSQL_USER']="root" #Especificar usuario
app.config['MYSQL_PASSWORD']="" #Especificar contraseña
app.config['MYSQL_DB']="prueba_consultorio" #Especificar a que base de datos

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

@app.route('/login', methods=['POST'])
def login():
    rfc = request.form['rfc']
    contrasena = request.form['contrasena']

    cs = mysql.connection.cursor()
    consulta = "SELECT rfc FROM `prueba_consultorio`.`medico` WHERE rfc = %s AND contrasena = %s"
    cs.execute(consulta, (rfc, contrasena))
    resultado = cs.fetchone()
    
    if resultado is not None:
        rol_query = "SELECT rol FROM `prueba_consultorio`.`medico` WHERE rfc = %s AND contrasena = %s"
        cs.execute(rol_query, (rfc, contrasena))
        rol_resultado = cs.fetchone()

        if rol_resultado is not None and rol_resultado[0] == "admin":
            session['rfc'] = resultado[0]
            return render_template('menu_admin.html')
        else:
            session['rfc'] = resultado[0]
            return render_template('menu_usuario.html')
    else:
        flash('RFC o contraseña incorrectos. Intente nuevamente.', 'error')
        return redirect(url_for('login'))


@app.route('/menu_admin')
#@login_required #Proteccion de rutas
def menu_admin():
        return render_template('menu_admin.html')

@app.route('/menu_usuario')
#@login_required #Proteccion de rutas
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

#El registro de paciente tiene ID foraneo
@app.route('/guardarPaciente',methods=['GET','POST'])
def guardarPaciente():
    if request.method=='POST': #Peticiones del usuario a traves del metodo POST
        _idmedico=request.form['medico']
        _exp=request.form['exp']
        #_idmedico=request.form['medico']
        _paciente=request.form['paciente']
        _ap=request.form['AP']
        _am=request.form['AM']
        _fn=request.form['FN']
        _af=request.form['AF']
        _al=request.form['AL']
        _ec=request.form['EC']
        #print(titulo,artista,anio)
        CS=mysql.connection.cursor()
        CS.execute('insert into exp_paciente(id_medico,exp,nombre,ap,am,fecha_nac,antec_fam,alergias,enf_cronicas) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (_idmedico,_exp,_paciente,_ap,_am,_fn,_af,_al,_ec)) #Para ejecutar codigo sql, y pasamos parametros
        mysql.connection.commit()

        flash('Paciente registrado exitosamente') #este mnsj se imprime en el CRUD de albums
        return redirect(url_for('guardarPaciente')) #Reedireccionamiento a la vista index

    c=mysql.connection.cursor()
    c.execute('select id_medico, concat (nombre, "",ap,"",am) as NombreCompleto from medico')
    medico=c.fetchall()
    return render_template('expediente_paciente.html', medico=medico)

@app.route('/guardarMedico',methods=['GET','POST'])
def guardarMedico():
    if request.method=='POST': #Peticiones del usuario a traves del metodo POST
        nombre=request.form['nombre']
        ap=request.form['AP']
        am=request.form['AM']
        rfc=request.form['RFC']
        cp=request.form['CP']
        ce=request.form['CE']
        Pass=request.form['pass']
        rol=request.form['rol']
        #print(titulo,artista,anio)
        CS=mysql.connection.cursor()
        CS.execute('insert into medico(nombre,ap,am,rfc,ced_prof,correo,contrasena,rol) values(%s,%s,%s,%s,%s,%s,%s,%s)',
                   (nombre,ap,am,rfc,cp,ce,Pass,rol)) #Para ejecutar codigo sql, y pasamos parametros
        mysql.connection.commit()

    flash('Médico registrado exitosamente')
    #return redirect(url_for('index')) #Reedireccionamiento a la vista index
    return render_template('registrar_medico.html')

#En la exploracion del paciente tiene como ID foraneo al expediente del paciente
@app.route('/exploracionPaciente',methods=['GET','POST'])
def exploracionPaciente():
    if request.method=='POST': #Peticiones del usuario a traves del metodo POST
        _idexp=request.form['pac']
        fechacita=request.form['user_fecha']
        peso=request.form['user_peso']
        altura=request.form['user_altura']
        temperatura=request.form['user_temperatura']
        fc=request.form['user_freccard']
        sto=request.form['user_ox']
        gluc=request.form['user_gluc']
        #print(titulo,artista,anio)
        CS=mysql.connection.cursor()
        CS.execute('insert into exploracion(id_expediente,fecha_cita,peso,altura,temperatura,frec_cardiaca,saturacion_ox,glucosa) values(%s,%s,%s,%s,%s,%s,%s,%s)',
                   (_idexp,fechacita,peso,altura,temperatura,fc,sto,gluc)) #Para ejecutar codigo sql, y pasamos parametros
        mysql.connection.commit()

        flash('Exploracion del paciente registrado exitosamente')
        return redirect(url_for('exploracionPaciente')) #Reedireccionamiento a la vista index
    
    c=mysql.connection.cursor()
    c.execute('select id_expediente, concat (nombre, "",ap,"",am) as NombreCompleto from exp_paciente')
    pac=c.fetchall()

    return render_template('exploracion_paciente.html',pac=pac)

#Diagnostico del paciente tiene como ID foraneo a exploracion del paciente, busqueda recomendada por fecha de cita (?)
@app.route('/diagnosticoPaciente',methods=['GET','POST'])
def diagnosticoPaciente():

    if request.method=='POST': #Peticiones del usuario a traves del metodo POST
        _idexp=request.form['pac']
        _sint=request.form['user_sint']
        _dx=request.form['user_dx']
        _med=request.form['user_med']
        _indicaciones=request.form['user_ind'] #Este es tratamiento
        _estudios=request.form['user_TS']
        CS=mysql.connection.cursor()
        CS.execute('insert into diagnostico(id_exploracion,sintomas,dx,medicamento,tratamiento,solic_estudios) values(%s,%s,%s,%s,%s,%s)',
                   (_idexp,_sint,_dx,_med,_indicaciones,_estudios)) #Para ejecutar codigo sql, y pasamos parametros
        mysql.connection.commit()

        flash('Diagnósticos del paciente registrado exitosamente')
        return redirect(url_for('diagnosticoPaciente')) #Reedireccionamiento a la vista index

    c=mysql.connection.cursor()
    c.execute('select exploracion.id_exploracion,exp_paciente.id_expediente, concat(nombre," ",ap," ",am) as Paciente FROM prueba_consultorio.exp_paciente INNER JOIN prueba_consultorio.exploracion ON exp_paciente.id_expediente = exploracion.id_expediente')
    pac=c.fetchall()
    return render_template('diagnostico_paciente.html',pac=pac)


@app.route('/editarMedico/<id>',methods=['GET','POST'])
def editarMedico(id):
    curEditar=mysql.connection.cursor()
    curEditar.execute('select * from medico where id_medico= %s', (id,))#Coma importante por que lo confunde con una tupla
    consultaID=curEditar.fetchone() #Para traer unicamente un registro

    return render_template('actualizar_medico.html',id=id, edmed=consultaID)

#Para actualizar/editar al medico
@app.route('/actualizarMedico/<id>',methods=['POST'])
def actualizarMedico(id):
    if request.method=='POST': #Peticiones del usuario a traves del metodo POST
        _nombre=request.form['user_nombre']
        _ap=request.form['user_AP']
        _am=request.form['user_AM']
        _rfc=request.form['user_RFC']
        _cp=request.form['user_CP']
        _ce=request.form['user_CE']
        _pass=request.form['user_pass']
        _rol=request.form['user_rol']
        #print(titulo,artista,anio)
        CS=mysql.connection.cursor()
        CS.execute('update medico set nombre=%s,ap=%s,am=%s,rfc=%s,ced_prof=%s,correo=%s,contrasena=%s,rol=%s where id_medico=%s',
                   (_nombre,_ap,_am,_rfc,_cp,_ce,_pass,_rol,id)) #Para ejecutar codigo sql, y pasamos parametros
        mysql.connection.commit()

    flash('Medico actualizado')
    return redirect(url_for('consultarMedico'))


#Para actualizar/editar al paciente

@app.route('/actualizarPaciente/<id>',methods=['GET','POST'])
def actualizarPaciente(id):
    editar=mysql.connection.cursor()
    editar.execute('select * from exp_paciente where id_expediente = %s',(id,))
    consulta=editar.fetchone() 
    return render_template('actualizar_paciente.html',id=id,edpac=consulta)
   

@app.route('/editarPaciente/<id>',methods=['POST'])
def editarPaciente(id):
    if request.method == 'POST':
       _nombre=request.form['paciente']
       _ap=request.form['user_AP']
       _am=request.form['user_AM']
       _fn=request.form['user_FN']
       _af=request.form['user_AF']
       _al=request.form['user_AL']
       _enfc=request.form['user_EC']

       curAct=mysql.connection.cursor()
       curAct.execute('update exp_paciente set nombre=%s, ap=%s, am=%s, fecha_nac=%s,antec_fam=%s,alergias=%s,enf_cronicas=%s where id_expediente = %s', (_nombre,_ap,_am,_fn,_af,_al,_enfc,id))
       mysql.connection.commit()

       flash('Paciente actualizado correctamente')
       return redirect(url_for('consultarPaciente'))

@app.route('/veliminar/<id>') 
def eliminarPac(id):
    eliminar=mysql.connection.cursor()
    eliminar.execute('select * from exp_paciente where id_expediente = %s',(id,))
    consulta=eliminar.fetchone()
 
    return render_template('eliminar_paciente.html',id=id,edpac=consulta)


@app.route('/eliminarPaciente/<id>',methods=['POST']) 
def eliminarPaciente(id):
    if request.method=='POST':
    
      eliminar=mysql.connection.cursor()
      eliminar.execute('select id_exploracion from exploracion where id_expediente =%s',(id,))
      id_exp=eliminar.fetchone()
      eliminar.execute('delete from diagnostico where id_exploracion = %s',(id_exp,))
      eliminar.execute('delete from exploracion where id_expediente =%s',(id,))
      eliminar.execute('delete from exp_paciente where id_expediente = %s',(id,))
      mysql.connection.commit()

    
    flash('Paciente eliminado correctamente')
    return redirect(url_for('consultarPaciente'))


@app.route('/buscarMedico',methods=['GET','POST'])
def buscarMedico():
    Bnom=request.form.get('user_nombre')
    curBusq=mysql.connection.cursor()
    curBusq.execute('select * from medico where nombre LIKE %s', (f'%{Bnom}%',))
    busqueda=curBusq.fetchall()
    return render_template('buscar_medico.html', busqmed=busqueda)

#Consultar medico que atiende, nombre completo del paciente, fecha nacimiento, 
# datos opcionales: ec,alergias, antecedentes con parametro de busqueda de expediente
@app.route('/buscarPaciente',methods=['GET','POST'])
def buscarPaciente():
    Bexp=request.form.get('user_exp')
    curBusq=mysql.connection.cursor()
    curBusq.execute('select medico.nombre,medico.ap,medico.am, exp_paciente.exp, exp_paciente.nombre,exp_paciente.ap,exp_paciente.am, exp_paciente.fecha_nac, exp_paciente.antec_fam,exp_paciente.alergias,exp_paciente.enf_cronicas from exp_paciente inner join medico on exp_paciente.id_medico=medico.id_medico where exp LIKE %s', (f'%{Bexp}%',))
    busqueda=curBusq.fetchall()
    return render_template('buscar_paciente.html', busqpac=busqueda)

#Consultar todas las citas que ha tenido el paciente, filtrada por el nombre del paciente y/o fecha de la cita
#Unicamente debe aparecer nombre del paciente y la fecha de la cita
@app.route('/consultarCita',methods=['GET','POST'])
def consultarCita():
    Cnom=request.form.get('user_nombre')
    curSelect=mysql.connection.cursor()
    '''curSelect.execute('select id from persona where nombre=? ',(Cnom,))
    consulta=curSelect.fetchone()'''
    #if consulta:
    curSelect.execute('select exp_paciente.id_expediente,exp_paciente.nombre,exp_paciente.ap, exp_paciente.am,exploracion.fecha_cita from exp_paciente inner join exploracion on exploracion.id_expediente=exp_paciente.id_expediente where exp_paciente.nombre LIKE %s',(f'%{Cnom}%',))
    Ccitas=curSelect.fetchall()
    return render_template('consultar_citas.html',tbcita=Ccitas)

@app.route('/consultarMedico',methods=['GET','POST'])
def consultarMedico():
    curSelect=mysql.connection.cursor()
    curSelect.execute('select * from medico')
    consulta=curSelect.fetchall()
    return render_template('consultar_medico.html', tbmedico=consulta)

@app.route('/consultarPaciente',methods=['GET','POST'])
def consultarPaciente():
    curSelect=mysql.connection.cursor()
    curSelect.execute('select * from exp_paciente')
    consulta=curSelect.fetchall()
    return render_template('consultar_paciente.html', tbpacientes=consulta)

@app.route('/descargarReceta',methods=['GET','POST'])
def descargarReceta():

    return render_template('descargar_receta.html')

#Eliminar medico
#Borrar para eliminar
@app.route('/borrarMedico/<id>')
def borrarMedico(id):
    curBorrar=mysql.connection.cursor()
    curBorrar.execute('select * from medico where id_medico= %s', (id,))#Coma importante por que lo confunde con una tupla
    consultaID=curBorrar.fetchone() #Para traer unicamente un registro

    return render_template('eliminar_medico.html', bmed=consultaID,id=id)

@app.route('/eliminarMedico/<id>',methods=['POST'])
def eliminarMedico(id):
    curDelete=mysql.connection.cursor()
    curDelete.execute('delete from medico where id_medico=%s', (id)) 
    mysql.connection.commit() #Para actualizar

    flash('Medico eliminado')
    return redirect(url_for('consultarMedico'))

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
    #app.run()
    app.config.from_object(config['development'])
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(port=5005,debug=True) #Procurar que sea un puerto desocupado, debug(prendido)