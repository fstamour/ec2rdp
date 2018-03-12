import base64
import pytest
from mock import mock_open, MagicMock

import ec2rdp.ec2rdp


@pytest.mark.parametrize('key_path, config_val, profile_name, exception', [
    pytest.param('/key.file', None, None, None),
    pytest.param(None, 'config_val', 'profile', None),
    pytest.param(None, None, None, IOError())
])
def test_get_key_location(mocker, key_path, config_val, profile_name, exception):

    expected = key_path if key_path else config_val

    mock_os = mocker.patch('ec2rdp.ec2rdp.os')
    mock_os.environ = {'AWS_PROFILE': profile_name} if profile_name else {}
    mock_os.path.expanduser.return_value = 'aws/config'

    mock_parser = MagicMock()
    mock_parser.get.return_value = expected
    mock_parser.get.side_effect = exception
    mock_parser_init = mocker.patch('ec2rdp.ec2rdp.ConfigParser')
    mock_parser_init.return_value = mock_parser

    if not exception:
        result = ec2rdp.ec2rdp.get_key_location(key_path)
        assert result == expected
    else:
        with pytest.raises(Exception):
            ec2rdp.ec2rdp.get_key_location(key_path)


@pytest.mark.parametrize('instance_id, exception',[
    pytest.param('Hello World!', None),
    pytest.param(None, IOError())
])
def test_get_ec2_data(mocker, instance_id, exception):

    expected = instance_id, instance_id

    mock_instance = MagicMock()
    mock_instance.public_dns_name = instance_id
    mock_instance.password_data.return_value = {
        'PasswordData': instance_id
    }
    mock_ec2 = MagicMock()
    mock_ec2.Instance.return_value = mock_instance
    mock_boto = mocker.patch('ec2rdp.ec2rdp.boto3')
    mock_boto.resource.return_value = mock_ec2
    mock_boto.resource.side_effect = exception

    if not exception:
        result = ec2rdp.ec2rdp.get_ec2_data(instance_id)
        assert result == expected
    else:
        with pytest.raises(Exception):
            ec2rdp.ec2rdp.get_ec2_data(instance_id)


@pytest.mark.parametrize('key_file, key_password, password_data, exception', [
    pytest.param('/key.file', 'password', base64.b64encode('Hello World!'), None),
    pytest.param(None, None, None, IOError())
])
def test_decrypt_password_data(mocker, key_file, key_password, password_data, exception):

    expected = password_data

    mock_os = mocker.patch('ec2rdp.ec2rdp.os')
    mock_os.path.expanduser.return_value = key_file

    mock_file = mock_open(read_data=password_data)
    mocker.patch('ec2rdp.ec2rdp.open', mock_file)

    mock_rsa = mocker.patch('ec2rdp.ec2rdp.RSA')
    mock_rsa.importKey.return_value = password_data

    mock_cipher = MagicMock()
    mock_cipher.decrypt.return_value = password_data
    mock_pkcs = mocker.patch('ec2rdp.ec2rdp.PKCS1_v1_5')
    mock_pkcs.new.return_value = mock_cipher

    if not exception:
        result = ec2rdp.ec2rdp.decrypt_password_data(key_file, key_password, password_data)
        assert result == expected
    else:
        with pytest.raises(Exception):
            ec2rdp.ec2rdp.decrypt_password_data(key_file, key_password, password_data)


@pytest.mark.parametrize('output, instance_id, exception', [
    pytest.param('/file.path', '1', None),
    pytest.param(None, '1', None),
    pytest.param(None, None, IOError())
])
def test_get_output(mocker, output, instance_id, exception):

    expected = output if output else '/{}.rdp'.format(instance_id)

    mock_os = mocker.patch('ec2rdp.ec2rdp.os')
    mock_os.path.join.return_value = '/{}.rdp'.format(instance_id)
    mock_os.path.dirname.return_value = '/'
    mock_os.path.expanduser.return_value = expected
    mock_os.path.expanduser.side_effect = exception

    if not exception:
        result = ec2rdp.ec2rdp.get_output(output, instance_id)
        assert result == expected
    else:
        with pytest.raises(Exception):
            ec2rdp.ec2rdp.get_output(output, instance_id)


@pytest.mark.parametrize('output, dns_name, exception',[
    pytest.param('/file.out', 'test.dns.name', None),
    pytest.param(None, None, IOError())
])
def test_write_rdp(mocker, output, dns_name, exception):

    content = [
        'auto connect:i:1\n',
        'full address:s:{}\n'.format(dns_name),
        'username:s:Administrator\n',
        'redirectclipboard:i:1\n',
        'prompt for credentials on client:i:1\n'
    ]

    mock_file = mock_open()
    mock_ctx = mocker.patch('ec2rdp.ec2rdp.open', mock_file)
    mock_ctx.side_effect = exception

    if not exception:
        ec2rdp.ec2rdp.write_rdp(output, dns_name)
        mock_file().writelines.assert_called_once_with(content)
    else:
        with pytest.raises(Exception):
            ec2rdp.ec2rdp.write_rdp(output, dns_name)


@pytest.mark.parametrize('password, exception', [
    pytest.param('password', None),
    pytest.param(None, IOError())
])
def test_password_to_clipboard(mocker, password, exception):
    mock_pyperclip = mocker.patch('ec2rdp.ec2rdp.pyperclip.copy')
    mock_pyperclip.side_effect = exception

    if not exception:
        ec2rdp.ec2rdp.password_to_clipboard(password)
        mock_pyperclip.assert_called_once_with(password)
    else:
        with pytest.raises(Exception):
            ec2rdp.ec2rdp.password_to_clipboard(password)

@pytest.mark.parametrize('args, exception', [
    pytest.param({
        'aws_profile': None,
        'aws_region': None,
        'aws_access_key_id': None,
        'aws_secret_access_key': None,
        'quick': True
    }, None),
    pytest.param({
        'aws_profile': '',
        'aws_region': '',
        'aws_access_key_id': '',
        'aws_secret_access_key': '',
        'quick': False
    }, None),
pytest.param({
        'aws_profile': '',
        'aws_region': '',
        'aws_access_key_id': '',
        'aws_secret_access_key': None,
        'quick': False
    }, None),
    pytest.param({
        'aws_profile': None,
        'aws_region': None,
        'aws_access_key_id': None,
        'aws_secret_access_key': None,
        'quick': False
    }, IOError())
])
def test_main(mocker, args, exception):

    mock_args = MagicMock()
    mock_args.aws_profile = args['aws_profile']
    mock_args.aws_region = args['aws_region']
    mock_args.aws_access_key_id = args['aws_access_key_id']
    mock_args.aws_secret_access_key = args['aws_secret_access_key']
    mock_args.quick = args['quick']

    mock_parser = MagicMock()
    mock_parser.parse_args.return_value = mock_args
    mock_argparse = mocker.patch('ec2rdp.ec2rdp.argparse')
    mock_argparse.ArgumentParser.return_value = mock_parser

    mocker.patch('ec2rdp.ec2rdp.getpass')

    mocker.patch('ec2rdp.ec2rdp.get_output')
    mock_ec2_data = mocker.patch('ec2rdp.ec2rdp.get_ec2_data')
    mock_ec2_data.return_value = '', ''
    mock_ec2_data.side_effect = exception
    mocker.patch('ec2rdp.ec2rdp.get_key_location')
    mocker.patch('ec2rdp.ec2rdp.decrypt_password_data')
    mocker.patch('ec2rdp.ec2rdp.write_rdp')
    mocker.patch('ec2rdp.ec2rdp.password_to_clipboard')

    if not exception:
        ec2rdp.ec2rdp.main()
    else:
        with pytest.raises(SystemExit):
            ec2rdp.ec2rdp.main()
