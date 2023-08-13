from flask import Flask, render_template, request, redirect,url_for,flash,session #Importar libreria
from flask_mysqldb import MySQL

app=Flask(__name__) 
  
app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root" 
app.config['MYSQL_PASSWORD']="" 
app.config['MYSQL_DB']="gestionmedica" 

app.secret_key='mysecretkey' 

mysql=MySQL(app)

@app.route('/')
def index():
  
    return render_template('index.html')

@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    if request.method == 'POST':
        Vusuario = request.form['nombre']
        Vpassword = request.form['password']
        
        usu = {
            'ABCD12345': 'Admin1',
            'EFGHI6789': 'Usuario1'
        }
        
        if Vusuario == 'ABCD12345':
            if Vusuario in usu and usu[Vusuario] == Vpassword:
                session['usuario'] = Vusuario
                return redirect(url_for('menu_admin'))
            else:
                flash('Usuario o contraseña incorrectos')
                return redirect(url_for('login'))
        elif Vusuario == 'EFGHI6789':
            if Vusuario in usu and usu[Vusuario] == Vpassword:
                session['nombre'] = Vusuario
                return redirect(url_for('menu_usuario'))
            else:
                flash('Usuario o contraseña incorrectos')
                return redirect(url_for('login'))
        else:
            flash('Usuario o contraseña incorrectos')
            return redirect(url_for('index'))
   
    # Si la solicitud es GET, renderiza la plantilla login.html
    return render_template('login.html')

 # HACER RUTAS A MENU_ADMIN Y MENU_USUARIO
@app.route('/menu_admin',methods=['GET','POST'])
def menu_admin():
    return render_template('menu_admin.html')

@app.route('/menu_usuario',methods=['GET','POST'])
def menu_usuario():
    return render_template('menu_usuario.html')

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

@app.route('/actualizarMedico',methods=['GET','POST'])
def actualizarMedico():

    return render_template('actualizar_medico.html')

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

@app.route('/consultarMedico',methods=['GET','POST'])
def consultarMedico():

    return render_template('consultar_medico.html')

@app.route('/consultarPaciente',methods=['GET','POST'])
def consultarPaciente():

    return render_template('consultar_paciente.html')

@app.route('/descargarReceta',methods=['GET','POST'])
def descargarReceta():

    return render_template('descargar_receta.html')

@app.route('/diagnosticoPaciente',methods=['GET','POST'])
def diagnosticoPaciente():

    return render_template('diagnostico_paciente.html')

@app.route('/eliminarMedico',methods=['GET','POST'])
def eliminarMedico():

    return render_template('eliminar_medico.html')

@app.route('/exploracionPaciente',methods=['GET','POST'])
def exploracionPaciente():

    return render_template('exploracion_paciente.html')

@app.route('/login',methods=['GET','POST'])
def login():

    return render_template('login.html')

#Ejecucion del servidor
if __name__=='__main__':
    app.run(port=5000,debug=True) #Procurar que sea un puerto desocupado, debug(prendido)