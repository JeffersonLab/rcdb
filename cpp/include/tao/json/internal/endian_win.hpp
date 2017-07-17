// Copyright (c) 2017 Dr. Colin Hirsch and Daniel Frey
// Please see LICENSE for license or visit https://github.com/taocpp/json/

#ifndef TAOCPP_JSON_INCLUDE_INTERNAL_ENDIAN_WIN_HPP
#define TAOCPP_JSON_INCLUDE_INTERNAL_ENDIAN_WIN_HPP

#include <cstdint>
#include <cstring>

#include <stdlib.h>  // TODO: Or is intrin.h the 'more correct' header for the _byteswap_foo() functions?

namespace tao
{
   namespace json
   {
      namespace internal
      {
         template< unsigned S >
         struct to_and_from_le
         {
            template< typename T >
            static T convert( const T t ) noexcept
            {
               return t;
            }
         };

         template< unsigned S >
         struct to_and_from_be;

         template<>
         struct to_and_from_be< 1 >
         {
            static std::uint8_t convert( const std::uint8_t n ) noexcept
            {
               return n;
            }
         };

         template<>
         struct to_and_from_be< 2 >
         {
            static std::uint16_t convert( const std::uint16_t n ) noexcept
            {
               return _byteswap_ushort( n );
            }
         };

         template<>
         struct to_and_from_be< 4 >
         {
            static float convert( float n ) noexcept
            {
               std::uint32_t u;
               std::memcpy( &u, &n, 4 );
               u = convert( u );
               std::memcpy( &n, &u, 4 );
               return n;
            }

            static std::uint32_t convert( const std::uint32_t n ) noexcept
            {
               return _byteswap_ulong( n );
            }
         };

         template<>
         struct to_and_from_be< 8 >
         {
            static double convert( double n ) noexcept
            {
               std::uint64_t u;
               std::memcpy( &u, &n, 8 );
               u = convert( u );
               std::memcpy( &n, &u, 8 );
               return n;
            }

            static std::uint64_t convert( const std::uint64_t n ) noexcept
            {
               return _byteswap_uint64( n );
            }
         };

      }  // namespace internal

   }  // namespace json

}  // namespace tao

#endif
