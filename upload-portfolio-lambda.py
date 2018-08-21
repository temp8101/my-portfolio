import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):

    s3 = boto3.resource("s3",config=Config(signature_version='s3v4'))
    sns = boto3.resource('sns')

    try:
        topic = sns.Topic('arn:aws:sns:us-east-2:431019014693:displayportfolio')

        portfolio_bucket = s3.Bucket('portfolio.dipens.com')
        build_bucket = s3.Bucket('portfoliobuild.dipens.com')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip',portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in  myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,
                ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print('Job Done')
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio Deployed successfully...")
    except:
        topic.publish(Subject="Portfolio Deployed Failed", Message="Portfolio was not Deployed successfully...")
        raise

    return 'Job done'
