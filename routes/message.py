from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.message import Message
from models.friendship import Friendship
from database import db
from sqlalchemy import or_, and_, desc, func

message_bp = Blueprint('message', __name__)


@message_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    """发送消息"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data or not data.get('receiver_id') or not data.get('content'):
            return jsonify({'error': '接收者ID和消息内容都是必需的'}), 400
        
        receiver_id = data['receiver_id']
        content = data['content'].strip()
        message_type = data.get('message_type', 'text')
        
        # 不能给自己发消息
        if current_user_id == receiver_id:
            return jsonify({'error': '不能给自己发消息'}), 400
        
        # 检查接收者是否存在
        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'error': '接收者不存在'}), 404
        
        # 检查是否为好友关系
        friendship = Friendship.query.filter(
            Friendship.user_id == current_user_id,
            Friendship.friend_id == receiver_id,
            Friendship.status == 'accepted'
        ).first()
        
        if not friendship:
            return jsonify({'error': '只能给好友发送消息'}), 403
        
        # 创建消息
        message = Message(
            sender_id=current_user_id,
            receiver_id=receiver_id,
            content=content,
            message_type=message_type
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': '消息发送成功',
            'data': message.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'发送消息失败: {str(e)}'}), 500


@message_bp.route('/history', methods=['GET'])
@jwt_required()
def get_message_history():
    """获取与某个好友的历史消息"""
    try:
        current_user_id = int(get_jwt_identity())
        friend_id = request.args.get('friend_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if not friend_id:
            return jsonify({'error': '好友ID是必需的'}), 400
        
        # 检查是否为好友关系
        friendship = Friendship.query.filter(
            Friendship.user_id == current_user_id,
            Friendship.friend_id == friend_id,
            Friendship.status == 'accepted'
        ).first()
        
        if not friendship:
            return jsonify({'error': '只能查看好友的聊天记录'}), 403
        
        # 查询聊天记录
        messages = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user_id, Message.receiver_id == friend_id),
                and_(Message.sender_id == friend_id, Message.receiver_id == current_user_id)
            )
        ).order_by(desc(Message.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 标记接收到的消息为已读
        Message.query.filter(
            Message.sender_id == friend_id,
            Message.receiver_id == current_user_id,
            Message.is_read == False
        ).update({'is_read': True})
        db.session.commit()
        
        message_list = []
        for message in messages.items:
            msg_dict = message.to_dict()
            # 添加发送者信息
            sender = User.query.get(message.sender_id)
            msg_dict['sender_username'] = sender.username if sender else 'Unknown'
            message_list.append(msg_dict)
        
        # 反转消息列表，使最新的消息在最后
        message_list.reverse()
        
        return jsonify({
            'messages': message_list,
            'pagination': {
                'page': messages.page,
                'pages': messages.pages,
                'per_page': messages.per_page,
                'total': messages.total,
                'has_next': messages.has_next,
                'has_prev': messages.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取聊天记录失败: {str(e)}'}), 500


@message_bp.route('/chats', methods=['GET'])
@jwt_required()
def get_chat_list():
    """获取聊天列表（最近联系人）"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # 获取所有涉及当前用户的消息，按聊天对象分组
        # 使用 Python 代码处理而不是复杂的 SQL 函数
        all_messages = Message.query.filter(
            or_(Message.sender_id == current_user_id, Message.receiver_id == current_user_id)
        ).order_by(desc(Message.created_at)).all()
        
        # 按聊天对象分组，保留最新消息
        chat_partners = {}
        for message in all_messages:
            # 确定聊天对象
            partner_id = message.receiver_id if message.sender_id == current_user_id else message.sender_id
            
            # 如果还没有这个聊天对象的记录，或者当前消息更新，则更新记录
            if partner_id not in chat_partners:
                chat_partners[partner_id] = message
        
        # 构建聊天列表
        chat_list = []
        for partner_id, last_message in chat_partners.items():
            chat_partner = User.query.get(partner_id)
            
            if chat_partner:
                # 计算未读消息数
                unread_count = Message.query.filter(
                    Message.sender_id == partner_id,
                    Message.receiver_id == current_user_id,
                    Message.is_read == False
                ).count()
                
                chat_info = {
                    'partner': chat_partner.to_dict(),
                    'last_message': last_message.to_dict(),
                    'unread_count': unread_count
                }
                chat_list.append(chat_info)
        
        # 按最后消息时间排序
        chat_list.sort(key=lambda x: x['last_message']['created_at'], reverse=True)
        
        return jsonify({
            'chats': chat_list,
            'count': len(chat_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取聊天列表失败: {str(e)}'}), 500


@message_bp.route('/last', methods=['GET'])
@jwt_required()
def get_last_message():
    """获取与某个好友的最后一条消息"""
    try:
        current_user_id = int(get_jwt_identity())
        friend_id = request.args.get('friend_id', type=int)
        
        if not friend_id:
            return jsonify({'error': '好友ID是必需的'}), 400
        
        # 检查是否为好友关系
        friendship = Friendship.query.filter(
            Friendship.user_id == current_user_id,
            Friendship.friend_id == friend_id,
            Friendship.status == 'accepted'
        ).first()
        
        if not friendship:
            return jsonify({'error': '只能查看好友的消息'}), 403
        
        # 查询最后一条消息
        last_message = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user_id, Message.receiver_id == friend_id),
                and_(Message.sender_id == friend_id, Message.receiver_id == current_user_id)
            )
        ).order_by(desc(Message.created_at)).first()
        
        if not last_message:
            return jsonify({'message': '暂无消息记录'}), 200
        
        # 添加发送者信息
        msg_dict = last_message.to_dict()
        sender = User.query.get(last_message.sender_id)
        msg_dict['sender_username'] = sender.username if sender else 'Unknown'
        
        return jsonify({'last_message': msg_dict}), 200
        
    except Exception as e:
        return jsonify({'error': f'获取最后消息失败: {str(e)}'}), 500


@message_bp.route('/mark_read', methods=['POST'])
@jwt_required()
def mark_messages_read():
    """标记消息为已读"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data or not data.get('sender_id'):
            return jsonify({'error': '发送者ID是必需的'}), 400
        
        sender_id = data['sender_id']
        
        # 标记来自指定发送者的所有未读消息为已读
        updated_count = Message.query.filter(
            Message.sender_id == sender_id,
            Message.receiver_id == current_user_id,
            Message.is_read == False
        ).update({'is_read': True})
        
        db.session.commit()
        
        return jsonify({
            'message': f'已标记 {updated_count} 条消息为已读'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'标记消息已读失败: {str(e)}'}), 500
