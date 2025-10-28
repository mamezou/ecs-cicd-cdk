# AWS SSOを使用したローカルセットアップ

このガイドでは、AWS SSOを使用してローカル環境からAWSリソースにアクセスする設定方法を説明します。

## 📋 前提条件

- AWS CLIバージョン2がインストールされていること
- 組織のAWS SSO設定が完了していること
- SSO開始URL、AWSリージョン、SSOリージョンの情報

## 🔐 AWS SSO設定手順

### 1. AWS SSOログイン設定

```bash
aws configure sso
```

以下の情報を入力します：

```
SSO session name (Recommended): my-sso-session
SSO start URL [None]: https://your-organization.awsapps.com/start
SSO region [None]: ap-northeast-1
SSO registration scopes [sso:account:access]:
```

### 2. アカウントとロールの選択

コマンド実行後、ブラウザが開いてSSOログインが求められます。ログイン後、以下を選択：

- 使用するAWSアカウントを選択
- 使用するロール（例：AdministratorAccess）を選択

### 3. CLI設定の完了

```
CLI default client Region [None]: ap-northeast-1
CLI default output format [None]: json
CLI profile name [AdministratorAccess-123456789012]: my-profile
```

### 4. 設定の確認

`~/.aws/config` ファイルに以下のような設定が追加されます：

```ini
[profile my-profile]
sso_session = my-sso-session
sso_account_id = 123456789012
sso_role_name = AdministratorAccess
region = ap-northeast-1
output = json

[sso-session my-sso-session]
sso_start_url = https://your-organization.awsapps.com/start
sso_region = ap-northeast-1
sso_registration_scopes = sso:account:access
```

## 🚀 使用方法

### SSOにログイン

```bash
aws sso login --profile my-profile
```

ブラウザが開き、認証を求められます。認証後、CLIからAWSリソースにアクセスできます。

### プロファイルの使用

```bash
# 環境変数で指定
export AWS_PROFILE=my-profile

# またはコマンドごとに指定
aws s3 ls --profile my-profile
cdk deploy --profile my-profile
```

### セッションの確認

```bash
aws sts get-caller-identity --profile my-profile
```

以下のような出力が表示されればOK：

```json
{
    "UserId": "AROAXXXXXXXXXXXXX:user@example.com",
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:assumed-role/AdministratorAccess/user@example.com"
}
```

## ⏰ セッション管理

AWS SSOセッションは通常8時間有効です。期限切れの場合は再度ログイン：

```bash
aws sso login --profile my-profile
```

## 🔧 CDKでの使用

CDKコマンド実行時にプロファイルを指定：

```bash
# Bootstrap
cdk bootstrap --profile my-profile

# Synthesize
cdk synth --profile my-profile

# Deploy
cdk deploy --profile my-profile

# Destroy
cdk destroy --profile my-profile
```

## 💡 ヒント

### デフォルトプロファイルの設定

毎回 `--profile` を指定したくない場合：

```bash
export AWS_PROFILE=my-profile
echo 'export AWS_PROFILE=my-profile' >> ~/.bashrc  # または ~/.zshrc
```

### 複数プロファイルの管理

複数のAWSアカウント/ロールを使い分ける場合：

```bash
# 開発環境
aws sso login --profile dev-profile

# 本番環境
aws sso login --profile prod-profile
```

### トラブルシューティング

SSOログインエラーが発生する場合：

```bash
# キャッシュをクリア
rm -rf ~/.aws/sso/cache/
rm -rf ~/.aws/cli/cache/

# 再度ログイン
aws sso login --profile my-profile
```

## 📚 参考リンク

- [AWS CLI SSO設定公式ドキュメント](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)
- [AWS SSO公式ドキュメント](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html)
