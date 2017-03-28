#!/usr/bin/python
# -*- coding: utf-8 -*-
# PIMC_PYLIB: the Python Library for Parametric Interval Markov Chains Verification
# Copyright (C) 2016 Ecole des Mines de Nantes
# Author: Anicet BART
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from core.readers import *
from model.dot_modeler import *

import web.controler.form_prism as form_prism

import cgitb, cgi
import Cookie
import os, json
cgitb.enable()
print('Content-type: text/html\n')

def get_content_uploaded_file (form, form_field):
    """This returns the text content of the uploaded file by an HTML form.
       The form is the result of the cgi.FieldStorage()
       The form_field is the name of the file input field from the HTML form.
       For example, the following form_field would be "file_1":
           <input name="file_1" type="file">
    """
    if not form.has_key(form_field): return 
    fileitem = form[form_field]
    if not fileitem.file: return

    content = ""
    while 1:
        chunk = fileitem.file.read(100000)
        if not chunk: break
        content += chunk
    return content


def view_getError(session):
  if 'error' in session and session['error']:
    return session['error']
  return None

       

# }

def ensure_html(string):
  # Replace "None" by empty string
  return string if string else ""



_session = {}
form_prism.loadForm(_session)

view = {}
view['form-prism'] = _session['dataPRISM']


print """
<html>

<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="">
  <meta name="author" content="">

  <title>PIMC PyLib - Live demo</title>

  <!-- Bootstrap Core CSS -->
  <link href="web/css/bootstrap.min.css" rel="stylesheet">

  <!-- Custom CSS -->
  <link href="web/css/modern-business.css" rel="stylesheet">

  <!-- Custom Fonts -->
  <link href="web/font-awesome/css/font-awesome.min.css" rel="stylesheet" type="text/css">

  <!-- Custom JS Libraries -->
  <script src="web/js/jquery.js"></script>
  <script src="web/js/viz-lite.js"></script>
"""

message = _session['pimc_string'] if 'pimc_string' in _session else None
if not(message):
  message = ""
else:
    networkType, pimc2 = TxtFileReader.readString(message)
    print("""
      <script>
        $( document ).ready(function() {
          console.log( "ready!" );
          $( '#draw-pimc' ).html(Viz(`""" + DotModeler.export(pimc2).replace('\\"', '\\\'') + """`));
        });
      </script>""")


print("""
</head>

<body>
 
    <!-- Navigation -->
    <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
        <div class="container">
            <!-- Brand and toggle get grouped for better mobile display -->
            <div class="navbar-header">
                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="index.html">Start Bootstrap</a>
            </div>
            <!-- Collect the nav links, forms, and other content for toggling -->
            <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                <ul class="nav navbar-nav navbar-right">
                    <li>
                        <a href="about.html">About</a>
                    </li>
                    <li class="active">
                        <a href="services.html">Services</a>
                    </li>
                    <li>
                        <a href="contact.html">Contact</a>
                    </li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">Portfolio <b class="caret"></b></a>
                        <ul class="dropdown-menu">
                            <li>
                                <a href="portfolio-1-col.html">1 Column Portfolio</a>
                            </li>
                            <li>
                                <a href="portfolio-2-col.html">2 Column Portfolio</a>
                            </li>
                            <li>
                                <a href="portfolio-3-col.html">3 Column Portfolio</a>
                            </li>
                            <li>
                                <a href="portfolio-4-col.html">4 Column Portfolio</a>
                            </li>
                            <li>
                                <a href="portfolio-item.html">Single Portfolio Item</a>
                            </li>
                        </ul>
                    </li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">Blog <b class="caret"></b></a>
                        <ul class="dropdown-menu">
                            <li>
                                <a href="blog-home-1.html">Blog Home 1</a>
                            </li>
                            <li>
                                <a href="blog-home-2.html">Blog Home 2</a>
                            </li>
                            <li>
                                <a href="blog-post.html">Blog Post</a>
                            </li>
                        </ul>
                    </li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">Other Pages <b class="caret"></b></a>
                        <ul class="dropdown-menu">
                            <li>
                                <a href="full-width.html">Full Width Page</a>
                            </li>
                            <li>
                                <a href="sidebar.html">Sidebar Page</a>
                            </li>
                            <li>
                                <a href="faq.html">FAQ</a>
                            </li>
                            <li>
                                <a href="404.html">404</a>
                            </li>
                            <li>
                                <a href="pricing.html">Pricing Table</a>
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
            <!-- /.navbar-collapse -->
        </div>
        <!-- /.container -->
    </nav>

    <!-- Page Content -->
    <div class="container">

        <!-- Page Heading/Breadcrumbs -->
        <div class="row">
            <div class="col-lg-12">
                <h1 class="page-header">Services
                    <small>Subheading</small>
                </h1>
            </div>


                <ul id="myTab" class="nav nav-tabs nav-justified">
                    <li class="active"><a href="#service-one" data-toggle="tab"><i class="fa fa-tree"></i> PRISM Code</a>
                    </li>
                    <li class=""><a href="#service-two" data-toggle="tab"><i class="fa fa-car"></i> Graph</a>
                    </li>
                    <li class=""><a href="#service-three" data-toggle="tab"><i class="fa fa-support"></i> Verification</a>
                    </li>
                    <li class=""><a href="#service-four" data-toggle="tab"><i class="fa fa-database"></i> Service Four</a>
                    </li>
                </ul>

                <div id="myTabContent" class="tab-content">
""")

# ------- Begin PRISM form -------
print("""
<div class="tab-pane fade active in" id="service-one">
  <h4>PRISM</h4>
  Insert your PRISM source code in the following area and click on the "Generate pIMC" button to construct the corresponding PIMC.
  Parameters and constants can be defined thanks to the form below.
  <form method="post">
    <div class="row text-center">
      <p><input class="btn btn-primary" type="submit" name="form_prism" value="Generate pIMC" /></p>
    </div>
""")

if view_getError(_session):
  print('<div class="col-lg-12 alert alert-danger"><strong>Error: </strong>%s</div>' % view_getError(_session))

print('<div class="row">')

# Constants form
print('<div class="col-lg-4">')
print('  <h5>Constant initialisations</h5>')
for i in range(4):
  name  = ensure_html(view['form-prism'].getConstant(i))
  value = ensure_html(view['form-prism'].getConstantValue(i))
  print('<div>')
  print('  <div class="col-xs-5 form-group"><input type="text" name="constant_name_%s" value="%s" class="form-control" placeholder="constant #%s"/></div>' % (i+1, name, i+1))
  print('  <div class="col-xs-1 form-group"><p class="form-control-static">=</p></div>')
  print('  <div class="col-xs-6 form-group"><input type="text" name="constant_value_%s" value="%s" class="form-control" placeholder="value"/></div>' % (i+1, value))
  print('</div>')
print('</div>')

# Parameters form
print('<div class="col-lg-4">')
print('  <h5>Parameter definitions</h5>')
for i in range(4):
  name  = ensure_html(view['form-prism'].getParameter(i))
  uid = ensure_html(view['form-prism'].getParameterUid(i))
  print('<div>')
  print('  <div class="col-xs-5 form-group"><input type="text" name="parameter_name_%s" value="%s" class="form-control" placeholder="parameter #%s"/></div>' % (i+1, name, i+1))
  print('  <div class="col-xs-1 form-group"><p class="form-control-static">&hArr;</p></div>')
  print('  <div class="col-xs-6 form-group"><input type="text" name="parameter_uid_%s" value="%s" class="form-control" placeholder="uid"/></div>' % (i+1, uid))
  print('</div>')
print('</div>')

# Parametric expressions
print('<div class="col-lg-4">')
print('  <h5>Parametric expressions</h5>')
for i in range(4):
  expression = ensure_html(view['form-prism'].getExpression(i))
  uid = ensure_html(view['form-prism'].getExpressionUid(i))
  print('<div>')
  print('  <div class="col-xs-5 form-group"><input type="text" name="expression_name_%s" value="%s" class="form-control" placeholder="expression #%s"/></div>' % (i+1, expression, i+1))
  print('  <div class="col-xs-1 form-group"><p class="form-control-static">&hArr;</p></div>')
  print('  <div class="col-xs-6 form-group"><input type="text" name="expression_uid_%s" value="%s" class="form-control" placeholder="uid"/></div>' % (i+1, uid))
  print('</div>')
print('</div>')

# PRISM source code form
print("""
      <div class="col-lg-12">
        <h5>PRISM Source Code</h5>             
        <textarea class="form-control" rows="25" name="source_code" style="font-family:monospace; font-size: 90%%">%s</textarea>
      </div>
    </div>
  </form>
</div>
""" % ensure_html(view['form-prism'].getSourceCode()))


# ------- Begin Graphical reresentation -------
print("""
  <div class="tab-pane fade" id="service-two">
    <h4>Graphical reresentation</h4>
    <div class="col-lg-12 text-center" id="draw-pimc"></div>
  </div>
""")


print("""
                    <div class="tab-pane fade" id="service-three">
                      <h4>Service Three</h4>
                      <div class="col-lg-4">
                        <h5>Existential Consistency</h5>
                        <div class="radio">
                          <label>
                            <input type="radio" name="optionsRadios" id="optionsRadios1" value="option1" />
                            VMCAI16 modelling encoded in SMT-LIB format
                          </label>
                        </div>
                        <div class="radio">
                          <label>
                            <input type="radio" name="optionsRadios" id="optionsRadios1" value="option2" />
                            Mec modelling encoded in SMT-LIB format
                          </label>
                        </div>
                        <div class="radio">
                          <label>
                            <input type="radio" name="optionsRadios" id="optionsRadios1" value="option3" />
                            Mec modelling encoded in CPLEX LP format 
                          </label>
                        </div>
                      </div>
                      <div class="col-lg-4">
                        <h5>Existential Qualitative Reachability</h5>
                        <div class="radio">
                          <label>
                            <input type="radio" name="optionsRadios" id="optionsRadios1" value="option5" />
                            Mer modelling encoded in SMT-LIB format
                          </label>
                        </div>
                        <div class="radio">
                          <label>
                            <input type="radio" name="optionsRadios" id="optionsRadios1" value="option6" />
                            Mer modelling encoded in CPLEX LP format 
                          </label>
                        </div>
                      </div>
                      <div class="col-lg-4">
                        <h5>Existential Quantitative Reachability</h5>
                        <div class="radio">
                          <label>
                            <input type="radio" name="optionsRadios" id="optionsRadios1" value="option5" />
                            Me<span class="over">r</span> modelling encoded in SMT-LIB format
                          </label>
                        </div>
                      </div>

                      <div class="col-lg-6">
                        <h5>Question</h5>
                        <div class="radio">
                          <label>
                            <input type="radio" name="optionsRadios" id="optionsRadios1" value="option4" checked="checked"/>
                            Satisfiability
                          </label>
                        </div>
                        <div class="radio">
                          <label>
                            <input type="radio" name="optionsRadios" id="optionsRadios1" value="option6" disabled="disabled"/>
                            Partitionning
                          </label>
                        </div>
                      </div>

                      <div class="col-lg-6">
                        <h5>Goal states</h5>
                        <div class="radio">
                          <label>
                            Select states by labelling.
                            <select class="form-control">
                              <option>target</option>
                              <option>no label</option>
                            </select>
                          </label>
                        </div>
                      </div>
                    </div>

                    <div class="tab-pane fade" id="service-four">
                        <h4>Service Four</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quae repudiandae fugiat illo cupiditate excepturi esse officiis consectetur, laudantium qui voluptatem. Ad necessitatibus velit, accusantium expedita debitis impedit rerum totam id. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Natus quibusdam recusandae illum, nesciunt, architecto, saepe facere, voluptas eum incidunt dolores magni itaque autem neque velit in. At quia quaerat asperiores.</p>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quae repudiandae fugiat illo cupiditate excepturi esse officiis consectetur, laudantium qui voluptatem. Ad necessitatibus velit, accusantium expedita debitis impedit rerum totam id. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Natus quibusdam recusandae illum, nesciunt, architecto, saepe facere, voluptas eum incidunt dolores magni itaque autem neque velit in. At quia quaerat asperiores.</p>
                    </div>
                </div>

        </div>



        <!-- Image Header -->
        <div class="row">

        </div>
        <!-- /.row -->

        <!-- Service Panels -->
        <!-- The circle icons use Font Awesome's stacked icon classes. For more information, visit http://fontawesome.io/examples/ -->
        <div class="row">
            <div class="col-lg-12">
                <h2 class="page-header">Services Panels</h2>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="panel panel-default text-center">
                    <div class="panel-heading">
                        <span class="fa-stack fa-5x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-tree fa-stack-1x fa-inverse"></i>
                        </span>
                    </div>
                    <div class="panel-body">
                        <h4>Service One</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p>
                        <a href="#" class="btn btn-primary">Learn More</a>
                    </div>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="panel panel-default text-center">
                    <div class="panel-heading">
                        <span class="fa-stack fa-5x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-car fa-stack-1x fa-inverse"></i>
                        </span>
                    </div>
                    <div class="panel-body">
                        <h4>Service Two</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p>
                        <a href="#" class="btn btn-primary">Learn More</a>
                    </div>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="panel panel-default text-center">
                    <div class="panel-heading">
                        <span class="fa-stack fa-5x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-support fa-stack-1x fa-inverse"></i>
                        </span>
                    </div>
                    <div class="panel-body">
                        <h4>Service Three</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p>
                        <a href="#" class="btn btn-primary">Learn More</a>
                    </div>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="panel panel-default text-center">
                    <div class="panel-heading">
                        <span class="fa-stack fa-5x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-database fa-stack-1x fa-inverse"></i>
                        </span>
                    </div>
                    <div class="panel-body">
                        <h4>Service Four</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p>
                        <a href="#" class="btn btn-primary">Learn More</a>
                    </div>
                </div>
            </div>
        </div>


        <!-- Service List -->
        <!-- The circle icons use Font Awesome's stacked icon classes. For more information, visit http://fontawesome.io/examples/ -->
        <div class="row">
            <div class="col-lg-12">
                <h2 class="page-header">Service List</h2>
            </div>
            <div class="col-md-4">
                <div class="media">
                    <div class="pull-left">
                        <span class="fa-stack fa-2x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-tree fa-stack-1x fa-inverse"></i>
                        </span> 
                    </div>
                    <div class="media-body">
                        <h4 class="media-heading">Service One</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo itaque ipsum sit harum.</p>
                    </div>
                </div>
                <div class="media">
                    <div class="pull-left">
                        <span class="fa-stack fa-2x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-car fa-stack-1x fa-inverse"></i>
                        </span> 
                    </div>
                    <div class="media-body">
                        <h4 class="media-heading">Service Two</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo itaque ipsum sit harum.</p>
                    </div>
                </div>
                <div class="media">
                    <div class="pull-left">
                        <span class="fa-stack fa-2x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-support fa-stack-1x fa-inverse"></i>
                        </span> 
                    </div>
                    <div class="media-body">
                        <h4 class="media-heading">Service Three</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo itaque ipsum sit harum.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="media">
                    <div class="pull-left">
                        <span class="fa-stack fa-2x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-database fa-stack-1x fa-inverse"></i>
                        </span> 
                    </div>
                    <div class="media-body">
                        <h4 class="media-heading">Service Four</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo itaque ipsum sit harum.</p>
                    </div>
                </div>
                <div class="media">
                    <div class="pull-left">
                        <span class="fa-stack fa-2x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-bomb fa-stack-1x fa-inverse"></i>
                        </span> 
                    </div>
                    <div class="media-body">
                        <h4 class="media-heading">Service Five</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo itaque ipsum sit harum.</p>
                    </div>
                </div>
                <div class="media">
                    <div class="pull-left">
                        <span class="fa-stack fa-2x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-bank fa-stack-1x fa-inverse"></i>
                        </span> 
                    </div>
                    <div class="media-body">
                        <h4 class="media-heading">Service Six</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo itaque ipsum sit harum.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="media">
                    <div class="pull-left">
                        <span class="fa-stack fa-2x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-paper-plane fa-stack-1x fa-inverse"></i>
                        </span> 
                    </div>
                    <div class="media-body">
                        <h4 class="media-heading">Service Seven</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo itaque ipsum sit harum.</p>
                    </div>
                </div>
                <div class="media">
                    <div class="pull-left">
                        <span class="fa-stack fa-2x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-space-shuttle fa-stack-1x fa-inverse"></i>
                        </span> 
                    </div>
                    <div class="media-body">
                        <h4 class="media-heading">Service Eight</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo itaque ipsum sit harum.</p>
                    </div>
                </div>
                <div class="media">
                    <div class="pull-left">
                        <span class="fa-stack fa-2x">
                              <i class="fa fa-circle fa-stack-2x text-primary"></i>
                              <i class="fa fa-recycle fa-stack-1x fa-inverse"></i>
                        </span> 
                    </div>
                    <div class="media-body">
                        <h4 class="media-heading">Service Nine</h4>
                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo itaque ipsum sit harum.</p>
                    </div>
                </div>
            </div>
        </div>
        <!-- /.row -->

        <hr>

        <!-- Footer -->
        <footer>
            <div class="row">
                <div class="col-lg-12">
                    <p>Copyright &copy; Your Website 2014</p>
                </div>
            </div>
        </footer>

    </div>
    <!-- /.container -->

    <!-- jQuery -->
    <script src="web/js/jquery.js"></script>

    <!-- Bootstrap Core JavaScript -->
    <script src="web/js/bootstrap.min.js"></script>
</body>
 
 </html>
 """)