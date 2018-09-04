# -*- coding: utf-8 -*-

"""Test dashboard browser class"""
import unittest
from src.modules.dashboard_browser import DataScraper

pagetext = """<!DOCTYPE html>
<html>
<head>
<script type="text/javascript">
  if (document.namespaces) {
    document.namespaces.add('v', 'urn:schemas-microsoft-com:vml', "#default#VML");
  }
</script>
<title>Choose Organization - Meraki Dashboard</title>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
<meta content="" name="keywords"/>
<meta content="Cisco Systems, Inc." name="description"/>
<meta content="true" name="MSSmartTagsPreventParsing"/>
<meta content="Copyright (c) 2018 Cisco Systems, Inc." name="Copyright"/>
<meta content="en-us" http-equiv="Content-Language"/>
<meta content="false" http-equiv="imagetoolbar"/>
<link href="/favicon.ico?1476982356" rel="Shortcut Icon" type="image/x-icon"/>
<script src="/javascripts/jquery-1.8.3.min.js?mtime=1526444738" type="text/javascript"></script>
<script src="/javascripts/jquery.cookie.min.js?mtime=1516130221" type="text/javascript"></script>
<script type="text/javascript">var $j = jQuery</script>
<script src="/javascripts/underscore.min.js?mtime=1524708484" type="text/javascript"></script>
<script>
    Mkiconf = window.Mkiconf || {}; Mkiconf.authenticity_token = "y3GRy1g6NvL0lxqumpPVsumS5GUBolKnQ1Yrg2EKQtE=";
  </script>
<script src="/javascripts/application.min.js?mtime=1535148211" type="text/javascript"></script>
<script src="/javascripts/json2.min.js?mtime=1516130220" type="text/javascript"></script>
<script type="text/javascript">
  Mkiconf = window.Mkiconf || {};
  Mkiconf.template_path = "/templates/application.html?mtime=1518650026";
</script>
<link href="/stylesheets/corpweb/style.css?1476982353" media="all" rel="stylesheet" type="text/css"/>
<link href="/stylesheets/minified/common_only.css?1534294326" media="all" rel="stylesheet" type="text/css"/>
<link href="/stylesheets/minified/login.css?1534294326" media="all" rel="stylesheet" type="text/css"/>
<script src="/javascripts/vendor.pack.js?mtime=1531428394" type="text/javascript"></script>
<script src="/javascripts/manage.pack.js?mtime=1535735896" type="text/javascript"></script> <link href="/stylesheets/jquery-themes/meraki/screen.css?1476982353" media="all" rel="stylesheet" type="text/css"/>
</head>
<body>
<noscript>
<div class="notice_explanation_container" id="javascript_failure_container">
<div class="notice_explanation bad">Your browser must have Javascript enabled to use Dashboard.</div>
</div>
<div style="clear:both"> </div>
</noscript>
<style>
  #cookie_failure_container {
    display: none;
  }

  html.no-cookies #cookie_failure_container {
    display: block;
  }
</style>
<div id="cookie_failure_container">
<div class="notice_explanation_container">
<div class="notice_explanation bad">Your browser must have cookies enabled to use Dashboard.</div>
</div>
</div>
<div style="min-width:450px;max-width:750px;margin:auto;">
<div id="login_header">
<a href="http://meraki.com/">
<img alt="Cisco Systems, Inc." border="0" src="/images/cisco-meraki.png?1476982351" style="width: 165px;margin-bottom:10px"/>
</a>
<div id="m_nav">
<span class="m_link">
<a href="https://account.meraki.com/login/logout">Return to Dashboard sign in</a>
</span>
</div>
</div>
<div id="login_main">
<div style="margin-bottom: 10px; clear: both;"></div>
<div style="clear:both">
<table><tr valign="top"><td>
<div id="login_form" style="padding:1em;margin-right:10px">
<div>
        Choose an organization
        <ul style="margin:0;padding-left:2em">
<li style="padding:.2em">
<a href="/login/org_choose?eid=0c9WHa">Gotham City</a> </li>
<li style="padding:.2em">
<a href="/login/org_choose?eid=B34SWb">Narnia</a> </li>
</ul>
</div>
</div>
</td></tr></table>
</div>
</div>
<div style="clear: both; height: 20px;"></div>
<style>
  #footer {
    display: flex;
    justify-content: space-between;
    color: #808080;
    border-top: 1px solid #cbcbcb;
    font-size: 0.9em;
    padding: 1em;
  }

  #footerLeft, #footerRight {
    display: flex;
    flex-direction: column;
  }

  #footerLeft > :not(:last-child),
  #footerRight > :not(:last-child) {
    margin-bottom: 0.5em;
  }

  #footerRight {
    align-items: flex-end;
  }

  #footerLeft {
    align-items: flex-start;
  }

  #footer #copyright {
    color: #ccc;
  }

  #china, #copyright, #languagePicker {
    display: flex;
  }

  #china > :not(:last-child),
  #copyright > :not(:last-child),
  #languagePicker > :not(:last-child) {
    margin-right: 1em;
  }

  #footer #china > a {
    display: flex;
    align-items: center;
  }

  #footer #languagePicker {
    align-items: center;
  }

  #footer .footerLink {
    color: #1795E6;
    text-decoration: none;
    padding-right:0.5em;
  }

  #footer .footerLink:hover {
    color: #1573a3;
    text-decoration: none;
  }

  #footer .icpLicense__link {
    width: 1.5em;
    margin-right:0.5em;
  }
</style>
<footer id="footer">
<div id="footerLeft">
</div>
<div id="footerRight">
<div id="copyright">
<a class="DashboardLoginPage__footerLink" href="http://www.meraki.com/support/#policies:eca">Terms</a>
<a class="DashboardLoginPage__footerLink" href="http://meraki.com/support/#policies:privacy">Privacy</a>
<span>© 2018 Cisco Systems, Inc.</span>
</div>
</div>
</footer>
</div>
<script type="text/javascript">//<![CDATA[
  
  //]]>
</script>
</body>
</html>"""


class TestDashboardBrowser(unittest.TestCase):
    def setUp(self):
        pass

    def something(self):
        """
        DataScraper.bypass_org_choose_page()
        DataScraper.filter_org_data()
        DataScraper.get_active_network_url()
        DataScraper.get_active_org_index()
        DataScraper.get_active_org_name()
        DataScraper.get_active_org_networks()
        DataScraper.get_browser()
        DataScraper.get_mkiconf_vars()
        DataScraper.get_org_names()
        DataScraper.get_url()
        DataScraper.org_data_setup()
        DataScraper.scrape_administered_orgs()
        DataScraper.scrape_ddns_and_ip()
        DataScraper.scrape_network_vars()
        DataScraper.scrape_psk()
        DataScraper.set_active_org_index()
        """