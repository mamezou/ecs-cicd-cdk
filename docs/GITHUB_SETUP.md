# GitHub設定ガイド

このガイドでは、GitHubとAWS CodePipelineを連携させるための設定方法を説明します。

## 📋 必要な設定

1. GitHubパーソナルアクセストークンの作成
2. AWS Secrets Managerへのトークン保存
3. CodeBuildへの認証情報登録

## 🔑 1. GitHubパーソナルアクセストークンの作成

### ステップ1: GitHubにアクセス

1. GitHubにログイン
2. 右上のプロフィールアイコンをクリック → **Settings**
3. 左サイドバーの一番下 → **Developer settings**
4. **Personal access tokens** → **Tokens (classic)**
5. **Generate new token** → **Generate new token (classic)**

### ステップ2: トークンの設定

以下の設定でトークンを作成：

**Note（メモ）**: `ecs-cicd-cdk-codepipeline` など識別可能な名前

**Expiration（有効期限）**: お好みで（推奨: 90日）

**Select scopes（スコープ選択）**: 以下にチェック

- ✅ `repo` - Full control of private repositories
  - ✅ `repo:status`
  - ✅ `repo_deployment`
  - ✅ `public_repo`
  - ✅ `repo:invite`
  - ✅ `security_events`
- ✅ `admin:repo_hook` - Full control of repository hooks
  - ✅ `write:repo_hook`
  - ✅ `read:repo_hook`
- ✅ `admin:org_hook` - Full control of organization hooks（組織リポジトリの場合）

### ステップ3: トークンをコピー

1. **Generate token** をクリック
2. 表示されたトークン（`ghp_...` で始まる文字列）を**必ずコピー**
   - ⚠️ このページを離れると二度と表示されません
   - 安全な場所に一時保存してください

## 🔐 2. AWS Secrets Managerへのトークン保存

### 方法1: AWS CLIを使用（推奨）

```bash
# プロファイルを設定（AWS SSO使用時）
export AWS_PROFILE=my-profile

# リージョンを設定
export AWS_REGION=ap-northeast-1

# シークレットを作成（<GITHUB-TOKEN>を実際のトークンに置換）
aws secretsmanager create-secret \
  --name /ecs-cicd-cdk/github/personal_access_token \
  --description "GitHub Personal Access Token for ECS CI/CD Pipeline" \
  --secret-string "<GITHUB-TOKEN>" \
  --region $AWS_REGION
```

### 方法2: AWSマネジメントコンソールを使用

1. AWS Secrets Manager コンソールにアクセス
2. **新しいシークレットを保存** をクリック
3. シークレットのタイプ: **その他のシークレットのタイプ**
4. キー/値のペアで入力:
   - プレーンテキストタブを選択
   - GitHubトークンを貼り付け
5. シークレット名: `/ecs-cicd-cdk/github/personal_access_token`
6. その他の設定はデフォルトのまま **次へ** → **保存**

### シークレット名のカスタマイズ

異なるシークレット名を使用する場合、CDKデプロイ時にパラメータで指定：

```bash
cdk deploy \
  --parameters githubUserName=<your-github-username> \
  --parameters githubPersonalTokenSecretName="/your/custom/secret/name"
```

### 保存確認

```bash
aws secretsmanager get-secret-value \
  --secret-id /ecs-cicd-cdk/github/personal_access_token \
  --region $AWS_REGION \
  --query SecretString \
  --output text
```

## 🔨 3. CodeBuildへの認証情報登録

CodeBuildがGitHubにWebhookを作成できるよう認証情報を登録：

```bash
aws codebuild import-source-credentials \
  --server-type GITHUB \
  --auth-type PERSONAL_ACCESS_TOKEN \
  --token <GITHUB-TOKEN> \
  --region $AWS_REGION
```

### 登録確認

```bash
aws codebuild list-source-credentials --region $AWS_REGION
```

以下のような出力が表示されればOK：

```json
{
    "sourceCredentialsInfos": [
        {
            "arn": "arn:aws:codebuild:ap-northeast-1:123456789012:token/github",
            "serverType": "GITHUB",
            "authType": "PERSONAL_ACCESS_TOKEN"
        }
    ]
}
```

## 📝 4. リポジトリのフォークまたはクローン

### 新規リポジトリとして使用する場合

このリポジトリを自分のGitHubアカウントにフォーク：

1. https://github.com/mamezou/ecs-cicd-cdk にアクセス
2. 右上の **Fork** ボタンをクリック
3. フォーク先のアカウントを選択

### ローカルにクローン

```bash
# フォークしたリポジトリをクローン
git clone https://github.com/<your-username>/ecs-cicd-cdk.git
cd ecs-cicd-cdk
```

## 🔄 CDKデプロイ時のパラメータ

GitHubユーザー名を指定してデプロイ：

```bash
cdk deploy \
  --profile my-profile \
  --parameters githubUserName=<your-github-username>
```

### 全パラメータを指定する場合

```bash
cdk deploy \
  --profile my-profile \
  --parameters githubUserName=<your-github-username> \
  --parameters githubRespository=ecs-cicd-cdk \
  --parameters githubPersonalTokenSecretName=/ecs-cicd-cdk/github/personal_access_token
```

## 🧹 クリーンアップ

### Secrets Managerからトークンを削除

```bash
# 削除をスケジュール（30日後に完全削除）
aws secretsmanager delete-secret \
  --secret-id /ecs-cicd-cdk/github/personal_access_token \
  --recovery-window-in-days 30 \
  --region $AWS_REGION

# 即座に削除（復元不可）
aws secretsmanager delete-secret \
  --secret-id /ecs-cicd-cdk/github/personal_access_token \
  --force-delete-without-recovery \
  --region $AWS_REGION
```

### CodeBuildの認証情報を削除

```bash
# ARNを取得
SOURCE_CRED_ARN=$(aws codebuild list-source-credentials \
  --query 'sourceCredentialsInfos[?serverType==`GITHUB`].arn' \
  --output text \
  --region $AWS_REGION)

# 削除
aws codebuild delete-source-credentials \
  --arn $SOURCE_CRED_ARN \
  --region $AWS_REGION
```

## ❓ トラブルシューティング

### エラー: "Repository not found"

- GitHubトークンのスコープが正しいか確認
- リポジトリ名、ユーザー名が正しいか確認

### エラー: "Access denied to secrets manager"

- AWS SSOセッションが有効か確認: `aws sso login --profile my-profile`
- Secrets Managerへのアクセス権限があるか確認

### Webhookが作成されない

- CodeBuildに認証情報が登録されているか確認
- GitHubトークンの `admin:repo_hook` 権限があるか確認

## 🔒 セキュリティのベストプラクティス

1. **トークンの最小権限**: 必要なスコープのみ選択
2. **有効期限の設定**: 定期的にトークンをローテーション
3. **トークンの安全な管理**: 
   - コードにハードコードしない
   - `.env` ファイルをgitignoreに追加
   - Secrets Managerで一元管理
4. **使用後の削除**: 不要になったトークンは即座に削除

## 📚 参考リンク

- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [AWS CodeBuild Source Credentials](https://docs.aws.amazon.com/codebuild/latest/userguide/sample-access-tokens.html)
