# ECS Fargate CI/CD ハンズオン
_FastAPIアプリケーションで学ぶAWS CI/CDパイプライン_

このハンズオンでは、AWS ECS Fargateにコンテナ化されたFastAPIアプリケーションをデプロイし、GitHubとAWS CodePipelineを連携させた継続的デリバリーパイプラインを構築します。

## 🎯 学習目標

このハンズオンを通じて以下を学びます：

- ✅ **ECS Fargate**: サーバーレスコンテナ実行環境の構築
- ✅ **AWS CodePipeline**: 継続的デリバリーパイプラインの実装
- ✅ **AWS CodeBuild**: Dockerイメージの自動ビルド
- ✅ **Infrastructure as Code**: AWS CDKによるインフラ管理
- ✅ **GitOps**: GitHubプッシュによる自動デプロイ

## � 前提条件

### 必須環境

- ✅ AWS SSOが設定済み・ログイン可能な状態
- ✅ GitHubアカウント
- ✅ Node.js 18以上がインストール済み
- ✅ AWS CLI v2がインストール済み
- ✅ Git

### インストール確認

```bash
# Node.js
node --version  # v18以上

# AWS CLI
aws --version   # 2.x以上

# Git
git --version
```

## �🚀 クイックスタート（30分）

### 1. リポジトリのフォーク

このリポジトリを自分のGitHubアカウントにフォーク:

1. 右上の **Fork** ボタンをクリック
2. フォーク先アカウントを選択

### 2. ローカルにクローン

```bash
git clone https://github.com/<your-username>/ecs-cicd-cdk.git
cd ecs-cicd-cdk
```

### 3. AWS SSOでログイン

```bash
# 既存のSSOプロファイルを使用
aws sso login --profile <your-sso-profile>

# プロファイルを環境変数に設定
export AWS_PROFILE=<your-sso-profile>
```

### 4. GitHubトークンの作成と保存

詳細は [docs/GITHUB_SETUP.md](./docs/GITHUB_SETUP.md) を参照。

```bash
# 1. GitHubでパーソナルアクセストークンを作成
#    Settings → Developer settings → Personal access tokens
#    必要なスコープ: repo, admin:repo_hook

# 2. Secrets Managerに保存
aws secretsmanager create-secret \
  --name /ecs-cicd-cdk/github/personal_access_token \
  --secret-string "<YOUR-GITHUB-TOKEN>"

# 3. CodeBuildに認証情報を登録
aws codebuild import-source-credentials \
  --server-type GITHUB \
  --auth-type PERSONAL_ACCESS_TOKEN \
  --token <YOUR-GITHUB-TOKEN>
```

### 5. CDKデプロイ

```bash
# 依存関係のインストール
npm install

# TypeScriptビルド
npm run build

# CDK Bootstrap（初回のみ）
cdk bootstrap

# デプロイ
cdk deploy --parameters githubUserName=<your-github-username>
```

デプロイには約10〜15分かかります。

### 6. アプリケーションにアクセス

デプロイ完了後、出力されるロードバランサーのURLにアクセス:

```
Outputs:
EcsCicdCdkStack.loadbalancerdns = EcsCi-ecsse-xxxxx.ap-northeast-1.elb.amazonaws.com
```

ブラウザで `http://<loadbalancer-dns>` を開いて動作確認。

## 🔄 CI/CDパイプラインのテスト

### コードを変更してプッシュ

```bash
# アプリコードを編集
cd docker-app/templates
vi hello.html  # タイトルなどを変更

# コミット＆プッシュ
git add .
git commit -m "Update app title"
git push origin main
```

### パイプラインの確認

1. **AWS Console** → **CodePipeline** で進行状況を確認
2. **Approve**ステージで手動承認
3. デプロイ完了後、ブラウザで変更を確認

## 🏗️ アーキテクチャ

```
GitHub (Push)
    ↓
CodePipeline (Source)
    ↓
CodeBuild (Build & Push to ECR)
    ↓
Manual Approval
    ↓
ECS Fargate (Deploy)
    ↓
Application Load Balancer
    ↓
FastAPI Application
```

## 📚 詳細ドキュメント

- 🔑 [GitHub設定](./docs/GITHUB_SETUP.md)
- 🔐 [AWS SSO参考情報](./docs/AWS_SSO_SETUP.md)（任意）

## 🧹 クリーンアップ

ハンズオン終了後、リソースを削除してコストを回避:

```bash
cdk destroy
```

確認プロンプトで `y` を入力。

## 💰 コスト概算

このハンズオンを1日実行した場合の概算コスト（東京リージョン）:

- Fargate: 約$1.2/日
- ALB: 約$0.7/日
- その他（ECR、CodePipeline等）: 約$0.1/日

**1日あたり合計**: 約$2

ハンズオン終了後は必ず`cdk destroy`でリソースを削除してください。

## ❓ トラブルシューティング

### デプロイが失敗する

```bash
# エラー内容を確認
cdk deploy --verbose

# スタック状態を確認
aws cloudformation describe-stacks --stack-name EcsCicdCdkStack
```

### ECSタスクが起動しない

```bash
# ECSコンソールでタスクの詳細を確認
# CloudWatch Logsでログを確認
```

### パイプラインがトリガーされない

- GitHubのWebhook設定を確認（Settings → Webhooks）
- CodeBuildの認証情報が登録されているか確認

