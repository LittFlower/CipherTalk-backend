from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.friendship import Friendship
from database import db
from sqlalchemy import or_, and_

friend_bp = Blueprint('friend', __name__)


@friend_bp.route('/add', methods=['POST'])
@jwt_required()
def add_friend():
    """添加好友"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data or not data.get('friend_username'):
            return jsonify({'error': '好友用户名是必需的'}), 400
        
        friend_username = data['friend_username'].strip()
        
        # 不能添加自己为好友
        current_user = User.query.get(current_user_id)
        if current_user.username == friend_username:
            return jsonify({'error': '不能添加自己为好友'}), 400
        
        # 查找要添加的好友
        friend = User.query.filter_by(username=friend_username).first()
        if not friend:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查是否已经是好友或已发送好友请求
        existing_friendship = Friendship.query.filter(
            or_(
                and_(Friendship.user_id == current_user_id, Friendship.friend_id == friend.id),
                and_(Friendship.user_id == friend.id, Friendship.friend_id == current_user_id)
            )
        ).first()
        
        if existing_friendship:
            if existing_friendship.status == 'accepted':
                return jsonify({'error': '已经是好友了'}), 400
            elif existing_friendship.status == 'pending':
                return jsonify({'error': '好友请求已发送，请等待对方同意'}), 400
        
        # 创建好友关系（双向）
        # 当前用户 -> 好友
        friendship1 = Friendship(user_id=current_user_id, friend_id=friend.id, status='accepted')
        # 好友 -> 当前用户
        friendship2 = Friendship(user_id=friend.id, friend_id=current_user_id, status='accepted')
        
        db.session.add(friendship1)
        db.session.add(friendship2)
        db.session.commit()
        
        return jsonify({
            'message': '好友添加成功',
            'friend': friend.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'添加好友失败: {str(e)}'}), 500


@friend_bp.route('/list', methods=['GET'])
@jwt_required()
def get_friends():
    """获取好友列表"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # 查询所有已接受的好友关系
        friendships = db.session.query(Friendship, User).join(
            User, User.id == Friendship.friend_id
        ).filter(
            Friendship.user_id == current_user_id,
            Friendship.status == 'accepted'
        ).order_by(User.username).all()
        
        friends = []
        for friendship, friend in friendships:
            friend_info = friend.to_dict()
            friend_info['friendship_created'] = friendship.created_at.isoformat() if friendship.created_at else None
            friends.append(friend_info)
        
        return jsonify({
            'friends': friends,
            'count': len(friends)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取好友列表失败: {str(e)}'}), 500


@friend_bp.route('/remove', methods=['POST'])
@jwt_required()
def remove_friend():
    """删除好友"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data or not data.get('friend_id'):
            return jsonify({'error': '好友ID是必需的'}), 400
        
        friend_id = data['friend_id']
        
        # 删除双向好友关系
        Friendship.query.filter(
            or_(
                and_(Friendship.user_id == current_user_id, Friendship.friend_id == friend_id),
                and_(Friendship.user_id == friend_id, Friendship.friend_id == current_user_id)
            )
        ).delete()
        
        db.session.commit()
        
        return jsonify({'message': '好友删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除好友失败: {str(e)}'}), 500


@friend_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    """搜索用户"""
    try:
        keyword = request.args.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({'error': '搜索关键词不能为空'}), 400
        
        # 搜索用户名包含关键词的用户
        users = User.query.filter(
            User.username.contains(keyword)
        ).limit(20).all()
        
        user_list = [user.to_dict() for user in users]
        
        return jsonify({
            'users': user_list,
            'count': len(user_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'搜索用户失败: {str(e)}'}), 500
